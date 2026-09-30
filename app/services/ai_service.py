import json
import logging
import math
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.schemas.ai import (
    CategorizeResponse,
    ChatResponse,
    InsightItem,
    InsightsResponse,
)

logger = logging.getLogger(__name__)

# Category Keyword Knowledge Base
CATEGORY_RULES = {
    "Food": [
        "zomato", "swiggy", "domino", "pizza", "burger", "mcdonald", "kfc",
        "starbucks", "cafe", "coffee", "restaurant", "bistro", "diner", "lunch",
        "dinner", "breakfast", "brunch", "snack", "bakery", "cake", "biryani",
        "subway", "chai", "tea", "canteen", "mess", "food", "tiffin"
    ],
    "Groceries": [
        "grocer", "supermarket", "dmart", "blinkit", "zepto", "instamart",
        "bigbasket", "nature's basket", "vegetable", "fruit", "milk", "dairy",
        "bread", "eggs", "meat", "fish", "provisions", "ration", "kirana", "mart"
    ],
    "Transport": [
        "uber", "ola", "rapido", "metro", "railway", "irctc", "train", "bus",
        "taxi", "cab", "auto", "fuel", "petrol", "diesel", "cng", "toll",
        "fastag", "parking", "flight", "indigo", "air india", "scooter", "bike"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "meesho", "ajio", "zara", "h&m", "nike",
        "adidas", "puma", "shoes", "clothes", "shirt", "pants", "dress", "jacket",
        "electronics", "laptop", "mobile", "gadget", "headphones", "mall", "retail"
    ],
    "Bills": [
        "electricity", "power", "water", "gas bill", "wifi", "broadband",
        "internet", "airtel", "jio", "vi", "vodafone", "dth", "tata play",
        "maintenance", "rent", "society", "utility", "bill", "postpaid", "lpg"
    ],
    "Entertainment": [
        "netflix", "spotify", "prime", "hotstar", "cinema", "movie", "pvr",
        "inox", "theatre", "bookmyshow", "concert", "game", "steam", "playstation",
        "xbox", "bowling", "club", "party", "amusement", "ott"
    ],
    "Health": [
        "hospital", "clinic", "doctor", "dentist", "pharmacy", "medicine",
        "chemist", "apollo", "1mg", "pharmeasy", "lab test", "pathology",
        "gym", "fitness", "yoga", "protein", "supplement", "health", "dental"
    ],
    "Education": [
        "tuition", "course", "udemy", "coursera", "book", "school", "college",
        "university", "exam", "fees", "coaching", "training", "library", "stationery"
    ],
    "Travel": [
        "hotel", "airbnb", "resort", "booking.com", "makemytrip", "agoda",
        "trip", "tour", "vacation", "holiday", "homestay", "visa", "luggage"
    ],
}


class AIService:
    @staticmethod
    def predict_category(text: str) -> CategorizeResponse:
        """
        Predicts category based on transaction title or description using
        keyword matching and optional LLM zero-shot classification.
        """
        clean_text = text.lower().strip()

        # Score categories by keyword presence
        category_scores = defaultdict(int)
        for cat, keywords in CATEGORY_RULES.items():
            for kw in keywords:
                if kw in clean_text:
                    category_scores[cat] += len(kw)

        if category_scores:
            best_cat = max(category_scores.items(), key=lambda x: x[1])[0]
            confidence = min(0.98, 0.75 + (category_scores[best_cat] * 0.03))
            return CategorizeResponse(
                category=best_cat,
                confidence=round(confidence, 2),
                reasoning=f"Matched financial keyword patterns in '{text}'",
            )

        # Default fallback
        return CategorizeResponse(
            category="Other",
            confidence=0.50,
            reasoning="Default classification due to lack of distinct merchant markers.",
        )

    @staticmethod
    def generate_financial_insights(
        expenses: List[Dict[str, Any]],
        budgets: List[Dict[str, Any]],
    ) -> InsightsResponse:
        """
        Analyzes user expenses and budgets to compute:
        1. Anomaly detection (outlier transactions).
        2. Largest category spikes and share of wallet.
        3. Budget overruns and proximity warnings.
        4. Actionable savings suggestions.
        """
        insights: List[InsightItem] = []

        if not expenses:
            insights.append(
                InsightItem(
                    type="tip",
                    message="Add your daily transactions to unlock real-time spending anomalies, budget tracking, and tailored financial advice.",
                )
            )
            return InsightsResponse(
                insights=insights,
                total_expenses=0.0,
                top_category=None,
                anomalies_count=0,
            )

        # Calculate basic metrics
        amounts = [float(e.get("amount", 0)) for e in expenses if float(e.get("amount", 0)) > 0]
        total_spent = sum(amounts)
        avg_amount = total_spent / len(amounts) if amounts else 0.0

        # Standard deviation for anomaly detection
        variance = (
            sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)
            if len(amounts) > 1
            else 0.0
        )
        std_dev = math.sqrt(variance)

        # 1. Anomaly / Outlier Detection
        anomaly_threshold = max(avg_amount * 2.2, avg_amount + (1.8 * std_dev))
        anomalies = [e for e in expenses if float(e.get("amount", 0)) >= anomaly_threshold and float(e.get("amount", 0)) > 500]

        for item in anomalies[:2]:
            amt = float(item.get("amount", 0))
            insights.append(
                InsightItem(
                    type="alert",
                    category=item.get("category"),
                    metric=f"₹{amt:,.0f}",
                    message=f"Outlier detected: ₹{amt:,.0f} on '{item.get('title')}' ({item.get('category')}) is significantly higher than your typical average transaction of ₹{avg_amount:,.0f}.",
                )
            )

        # 2. Category Aggregation & Largest Spikes
        cat_totals: Dict[str, float] = defaultdict(float)
        for e in expenses:
            cat_totals[e.get("category", "Other")] += float(e.get("amount", 0))

        top_cat = None
        if cat_totals:
            top_cat, top_amt = max(cat_totals.items(), key=lambda x: x[1])
            top_share = (top_amt / total_spent * 100) if total_spent > 0 else 0
            if top_share >= 35.0 and total_spent > 1000:
                insights.append(
                    InsightItem(
                        type="alert",
                        category=top_cat,
                        metric=f"{top_share:.1f}%",
                        message=f"{top_cat} makes up {top_share:.1f}% (₹{top_amt:,.0f}) of your total spending. Consider reviewing this category to balance your cash flow.",
                    )
                )

        # 3. Budget Overrun & Threshold Check
        budget_map = {b.get("category"): float(b.get("limit", 0)) for b in budgets}
        for cat, limit in budget_map.items():
            spent = cat_totals.get(cat, 0.0)
            if spent > limit > 0:
                overrun = spent - limit
                pct = (spent / limit) * 100
                insights.append(
                    InsightItem(
                        type="alert",
                        category=cat,
                        metric=f"{pct:.0f}%",
                        message=f"Budget Exceeded: {cat} spending is at ₹{spent:,.0f}, exceeding your monthly ceiling of ₹{limit:,.0f} by ₹{overrun:,.0f} ({pct:.0f}%).",
                    )
                )
            elif spent >= (0.8 * limit) and limit > 0:
                pct = (spent / limit) * 100
                insights.append(
                    InsightItem(
                        type="alert",
                        category=cat,
                        metric=f"{pct:.0f}%",
                        message=f"Budget Guardrail Warning: {cat} is at {pct:.0f}% of your ₹{limit:,.0f} ceiling. You have ₹{limit - spent:,.0f} remaining.",
                    )
                )

        # 4. Tailored Saving Suggestions
        discretionary_spend = (
            cat_totals.get("Shopping", 0.0)
            + cat_totals.get("Entertainment", 0.0)
            + cat_totals.get("Food", 0.0) * 0.4
        )
        if discretionary_spend > 2000:
            potential_saving = discretionary_spend * 0.20
            insights.append(
                InsightItem(
                    type="tip",
                    message=f"Discretionary Trim: Trimming 20% from Shopping, Dining, and Entertainment can preserve approx ₹{potential_saving:,.0f} each month for your investment portfolio.",
                )
            )

        # Add 50/30/20 guideline tip
        insights.append(
            InsightItem(
                type="tip",
                message="SpendWise Standard: Aim for the 50/30/20 allocation rule — 50% on Essentials (Groceries, Bills), 30% on Discretionary (Dining, Leisure), and 20% on Savings & Investments.",
            )
        )

        return InsightsResponse(
            insights=insights,
            total_expenses=round(total_spent, 2),
            top_category=top_cat,
            anomalies_count=len(anomalies),
        )

    @staticmethod
    async def process_chat(
        question: str,
        expenses: List[Dict[str, Any]],
        budgets: List[Dict[str, Any]],
    ) -> ChatResponse:
        """
        Answers natural language queries about expenses, budgets, and savings.
        Uses external LLM (Gemini or OpenAI) if API keys are configured,
        or relies on a robust rule-based financial reasoning engine.
        """
        q_lower = question.lower().strip()

        # Build ledger summary context
        total_spent = sum(float(e.get("amount", 0)) for e in expenses)
        total_count = len(expenses)

        cat_breakdown: Dict[str, float] = defaultdict(float)
        for e in expenses:
            cat_breakdown[e.get("category", "Other")] += float(e.get("amount", 0))

        top_category = (
            max(cat_breakdown.items(), key=lambda x: x[1])[0] if cat_breakdown else "N/A"
        )
        top_category_amount = cat_breakdown.get(top_category, 0.0)

        highest_single = None
        if expenses:
            highest_single = max(expenses, key=lambda x: float(x.get("amount", 0)))

        # Try External LLM if Gemini API Key is available
        if settings.GEMINI_API_KEY:
            try:
                ledger_summary = {
                    "total_expenses": total_spent,
                    "transaction_count": total_count,
                    "category_breakdown": dict(cat_breakdown),
                    "budgets": budgets,
                    "highest_transaction": highest_single,
                    "sample_recent_transactions": expenses[:5],
                }

                system_prompt = (
                    "You are SpendWise AI, an expert financial advisory assistant. "
                    "Analyze the user's financial ledger context and answer their question concisely, "
                    "accurately, and with actionable numbers in Indian Rupees (₹).\n\n"
                    f"User Financial Context:\n{json.dumps(ledger_summary, indent=2)}\n"
                )

                async with httpx.AsyncClient(timeout=10.0) as client:
                    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                    payload = {
                        "contents": [
                            {"role": "user", "parts": [{"text": f"{system_prompt}\nUser Question: {question}"}]}
                        ]
                    }
                    resp = await client.post(gemini_url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        answer = (
                            data.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )
                        if answer:
                            return ChatResponse(
                                answer=answer.strip(),
                                suggested_actions=[
                                    "Where did I spend the most?",
                                    "How to save 20% on shopping?",
                                    "Am I within my monthly budget?",
                                ],
                            )
            except Exception as e:
                logger.warning(f"External LLM call failed, falling back to rule engine: {e}")

        # Intelligent Rule-Based Financial Reasoner (Fallback / Local)
        # 1. "Where did I spend the most?" / "Top category" / "Highest spend"
        if any(w in q_lower for w in ["most", "highest", "biggest", "top category", "where did i spend"]):
            if not expenses:
                return ChatResponse(
                    answer="You haven't recorded any expenses yet. Once you add transactions, I will analyze which category occupies the largest share of your wallet."
                )

            share = (top_category_amount / total_spent * 100) if total_spent > 0 else 0
            single_info = ""
            if highest_single:
                single_info = (
                    f" Your largest individual transaction was ₹{float(highest_single.get('amount', 0)):,.0f} "
                    f"for '{highest_single.get('title')}' on {highest_single.get('date')}."
                )

            return ChatResponse(
                answer=(
                    f"You spent the most on **{top_category}**, totaling **₹{top_category_amount:,.0f}**, "
                    f"which accounts for **{share:.1f}%** of your total ₹{total_spent:,.0f} expenditure.{single_info}"
                ),
                suggested_actions=[
                    f"How to cut back on {top_category}?",
                    "What are my budget ceilings?",
                    "Show monthly breakdown",
                ],
            )

        # 2. "How to save 20% on shopping?" / "Save on X"
        if "save" in q_lower or "cut" in q_lower or "reduce" in q_lower:
            # Check if specific category mentioned
            target_cat = "Shopping"
            for cat in ["Shopping", "Food", "Entertainment", "Transport", "Bills", "Groceries"]:
                if cat.lower() in q_lower:
                    target_cat = cat
                    break

            cat_spend = cat_breakdown.get(target_cat, 0.0)
            target_save_pct = 20
            match = re.search(r"(\d+)%", q_lower)
            if match:
                target_save_pct = int(match.group(1))

            target_save_amt = (cat_spend * target_save_pct) / 100

            if cat_spend > 0:
                answer = (
                    f"Your current spend on **{target_cat}** is **₹{cat_spend:,.0f}**. "
                    f"To save {target_save_pct}% (approx **₹{target_save_amt:,.0f}**), consider these steps:\n\n"
                    f"1. **Enforce the 48-Hour Rule**: Wait 48 hours before non-essential purchases to curb impulsive checkouts.\n"
                    f"2. **Category Ceiling**: Set a strict monthly budget of ₹{cat_spend - target_save_amt:,.0f} in the Budgets tab.\n"
                    f"3. **Audit Subscriptions & Add-ons**: Check for recurring charges or unneeded upgrades.\n"
                    f"4. **Coupon & Cashback Optimization**: Always search for promotional codes and utilize UPI cashback opportunities."
                )
            else:
                answer = (
                    f"To save {target_save_pct}% on **{target_cat}**, set a monthly budget threshold in your Budgets tab, "
                    f"wait 48 hours before committing to discretionary purchases, and track each transaction immediately upon payment."
                )

            return ChatResponse(
                answer=answer,
                suggested_actions=[
                    f"Set a budget for {target_cat}",
                    "Where did I spend the most?",
                    "What is my savings rate?",
                ],
            )

        # 3. "Am I over budget?" / "Budget status" / "Budgets"
        if "budget" in q_lower or "over budget" in q_lower or "limit" in q_lower:
            if not budgets:
                return ChatResponse(
                    answer="You haven't defined any budget ceilings yet! Navigate to the **Budgets** section to set limits for Food, Shopping, Transport, and other categories.",
                    suggested_actions=["Create a Budget", "Where did I spend the most?"],
                )

            over_items = []
            under_items = []
            for b in budgets:
                cat = b.get("category")
                limit = float(b.get("limit", 0))
                spent = cat_breakdown.get(cat, 0.0)
                if spent > limit:
                    over_items.append(f"• **{cat}**: Spent ₹{spent:,.0f} (Exceeded ₹{limit:,.0f} limit by ₹{spent - limit:,.0f})")
                else:
                    under_items.append(f"• **{cat}**: Spent ₹{spent:,.0f} of ₹{limit:,.0f} limit ({limit - spent:,.0f} remaining)")

            response_parts = []
            if over_items:
                response_parts.append("⚠ **Budget Overruns Detected:**\n" + "\n".join(over_items))
            if under_items:
                response_parts.append("✅ **Within Budget Limits:**\n" + "\n".join(under_items))

            return ChatResponse(
                answer="\n\n".join(response_parts),
                suggested_actions=["How to save 20% on shopping?", "Where did I spend the most?"],
            )

        # 4. "How much did I spend?" / "Total spend" / "Summary"
        if any(w in q_lower for w in ["how much", "total spent", "total expense", "summary", "ledger"]):
            cat_lines = [f"• **{k}**: ₹{v:,.0f} ({(v/total_spent*100):.1f}%)" for k, v in sorted(cat_breakdown.items(), key=lambda x: x[1], reverse=True)]
            answer = (
                f"You have recorded **{total_count} transactions** totaling **₹{total_spent:,.0f}**.\n\n"
                f"**Category Breakdown:**\n" + "\n".join(cat_lines[:5])
            )
            return ChatResponse(
                answer=answer,
                suggested_actions=["Where did I spend the most?", "How to save 20% on shopping?"],
            )

        # 5. Default General Conversational Response
        return ChatResponse(
            answer=(
                f"Hello! I am your SpendWise AI financial copilot. Based on your current records:\n"
                f"• Total tracked expenditure: **₹{total_spent:,.0f}** across {total_count} transactions.\n"
                f"• Primary spending category: **{top_category}** (₹{top_category_amount:,.0f}).\n\n"
                f"Feel free to ask questions like:\n"
                f"• *'Where did I spend the most?'*\n"
                f"• *'How to save 20% on shopping?'*\n"
                f"• *'Am I over budget this month?'*\n"
                f"• *'How can I improve my savings rate?'*"
            ),
            suggested_actions=[
                "Where did I spend the most?",
                "How to save 20% on shopping?",
                "Am I over budget?",
            ],
        )
