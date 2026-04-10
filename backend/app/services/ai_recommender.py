"""AI-based routing recommendation engine."""
from app.utils.metrics import metrics_collector
from app.services.cost_engine import compare_costs


class AIRecommender:
    """Recommends optimal routing strategies based on traffic patterns."""

    def analyze_and_recommend(self, user_lat: float, user_lon: float,
                               traffic_rps: float = 100) -> dict:
        """Analyze traffic and recommend best routing strategy."""
        metrics = metrics_collector.snapshot()
        cost_comparison = compare_costs(max(int(traffic_rps), 1))

        # Scoring model
        scores = {
            "default": 0.0,
            "cdn_only": 0.0,
            "global_accelerator": 0.0,
            "optimized": 0.0,
        }
        reasoning = []

        # Factor 1: Latency sensitivity
        if metrics["avg_latency_ms"] > 150:
            scores["global_accelerator"] += 35
            scores["optimized"] += 40
            reasoning.append(
                f"High average latency ({metrics['avg_latency_ms']:.0f}ms) detected — "
                "Global Accelerator recommended for backbone optimization"
            )
        elif metrics["avg_latency_ms"] > 80:
            scores["global_accelerator"] += 20
            scores["optimized"] += 25
            scores["cdn_only"] += 15
            reasoning.append(
                f"Moderate latency ({metrics['avg_latency_ms']:.0f}ms) — "
                "CDN + Accelerator can reduce by ~50%"
            )
        else:
            scores["default"] += 20
            scores["cdn_only"] += 15
            reasoning.append(
                f"Low latency ({metrics['avg_latency_ms']:.0f}ms) — "
                "default routing is acceptable"
            )

        # Factor 2: Cache efficiency
        if metrics["cache_hit_ratio"] > 0.6:
            scores["cdn_only"] += 25
            scores["optimized"] += 20
            reasoning.append(
                f"High cache hit ratio ({metrics['cache_hit_ratio']:.0%}) — "
                "CDN is effective for this traffic pattern"
            )
        elif metrics["cache_hit_ratio"] > 0.3:
            scores["cdn_only"] += 15
            scores["optimized"] += 15
            reasoning.append(
                f"Moderate cache ratio ({metrics['cache_hit_ratio']:.0%}) — "
                "CDN provides partial benefit"
            )
        else:
            scores["global_accelerator"] += 10
            reasoning.append(
                f"Low cache ratio ({metrics['cache_hit_ratio']:.0%}) — "
                "mostly dynamic content, CDN less effective"
            )

        # Factor 3: Traffic volume / cost sensitivity
        if traffic_rps > 500:
            scores["optimized"] += 30
            scores["cdn_only"] += 20
            reasoning.append(
                f"High traffic ({traffic_rps} RPS) — "
                "optimized routing provides best cost efficiency at scale"
            )
        elif traffic_rps > 100:
            scores["cdn_only"] += 15
            scores["optimized"] += 15
            reasoning.append(
                f"Moderate traffic ({traffic_rps} RPS) — "
                "CDN recommended for cost savings"
            )
        else:
            scores["default"] += 15
            reasoning.append(
                f"Low traffic ({traffic_rps} RPS) — "
                "infrastructure overhead may outweigh benefits"
            )

        # Factor 4: Geographic distribution
        active_regions = metrics.get("active_regions", 0)
        if active_regions > 3:
            scores["global_accelerator"] += 20
            scores["optimized"] += 25
            reasoning.append(
                f"Traffic across {active_regions} regions — "
                "Global Accelerator excels at multi-region routing"
            )

        # Determine winner
        best = max(scores, key=scores.get)
        max_score = max(scores.values())
        total_score = sum(scores.values()) or 1
        confidence = round(max_score / total_score, 3)

        # Predicted improvements
        latency_savings = {
            "default": 0,
            "cdn_only": 25,
            "global_accelerator": 45,
            "optimized": 62,
        }
        cost_savings = {
            "default": 0,
            "cdn_only": 30,
            "global_accelerator": 10,
            "optimized": 35,
        }

        base_latency = max(metrics["avg_latency_ms"], 100)
        predicted_latency = base_latency * (1 - latency_savings[best] / 100)

        # Alternatives
        alternatives = []
        sorted_strategies = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for strategy, score in sorted_strategies[1:]:
            alternatives.append({
                "strategy": strategy,
                "score": round(score, 2),
                "latency_savings_pct": latency_savings[strategy],
                "cost_savings_pct": cost_savings[strategy],
            })

        return {
            "recommended_strategy": best,
            "confidence": confidence,
            "predicted_latency_ms": round(predicted_latency, 2),
            "predicted_cost_usd": cost_comparison.get(best, {}).get("total_usd", 0),
            "latency_savings_pct": latency_savings[best],
            "cost_savings_pct": cost_savings[best],
            "reasoning": reasoning,
            "alternatives": alternatives,
        }

    def predict_savings(self, current_rps: float = 100) -> dict:
        """Predict cost and latency savings for each strategy."""
        cost_data = compare_costs(int(current_rps * 3600))  # hourly cost
        return {
            "hourly_costs": cost_data,
            "monthly_projection": {
                mode: {
                    "cost_usd": round(data["total_usd"] * 720, 4),  # 720 hours/month
                }
                for mode, data in cost_data.items()
                if isinstance(data, dict) and "total_usd" in data
            },
            "savings_pct": cost_data.get("savings_pct", 0),
        }


# Singleton
ai_recommender = AIRecommender()
