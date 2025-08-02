"""
Agentic AI Implementation
========================

This is an agentic AI system that demonstrates autonomous behavior, planning,
tool use, memory, and adaptive decision-making capabilities.
"""

import openai
import json
import asyncio
import aiofiles
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

# Reuse ticket structures from traditional agent
from ai_agent import CustomerTicket, TicketPriority, TicketStatus

class ActionType(Enum):
    ANALYZE = "analyze"
    RESEARCH = "research"
    COMMUNICATE = "communicate"
    ESCALATE = "escalate"
    LEARN = "learn"
    PLAN = "plan"
    EXECUTE = "execute"

@dataclass
class Action:
    type: ActionType
    description: str
    parameters: Dict[str, Any]
    confidence: float
    expected_outcome: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Memory:
    ticket_id: str
    customer_context: Dict[str, Any]
    actions_taken: List[Action]
    outcomes: List[str]
    lessons_learned: List[str]
    sentiment_analysis: Dict[str, float]
    resolution_time: Optional[timedelta] = None
    satisfaction_score: Optional[float] = None

@dataclass
class Goal:
    objective: str
    priority: int
    deadline: Optional[datetime]
    success_criteria: List[str]
    current_progress: float = 0.0
    sub_goals: List['Goal'] = field(default_factory=list)

class AgenticAI:
    """
    Agentic AI System - Autonomous, adaptive, and intelligent
    
    Characteristics:
    - Autonomous planning and decision-making
    - Dynamic tool selection and usage
    - Learning from interactions and outcomes
    - Contextual memory and reasoning
    - Goal-oriented behavior
    - Proactive problem-solving
    - Adaptive to new scenarios
    """
    
    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name
        
        # Initialize components
        self.memory_store = self._initialize_memory()
        self.knowledge_vector_db = self._initialize_vector_db()
        self.tools = self._initialize_tools()
        self.goals = []
        self.context_window = []
        
        # Learning and adaptation
        self.performance_metrics = {}
        self.learned_patterns = {}
        self.adaptation_threshold = 0.7
        
        # Embeddings for semantic understanding
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def _initialize_memory(self) -> Dict[str, Memory]:
        """Initialize persistent memory system"""
        return {}
    
    def _initialize_vector_db(self):
        """Initialize vector database for knowledge storage"""
        client = chromadb.Client()
        return client.create_collection(
            name="customer_support_knowledge",
            metadata={"description": "Dynamic knowledge base for customer support"}
        )
    
    def _initialize_tools(self) -> Dict[str, Callable]:
        """Initialize available tools for the agent"""
        return {
            "sentiment_analyzer": self._analyze_sentiment,
            "knowledge_retriever": self._retrieve_knowledge,
            "escalation_predictor": self._predict_escalation,
            "response_generator": self._generate_contextual_response,
            "customer_profiler": self._profile_customer,
            "solution_recommender": self._recommend_solutions,
            "learning_engine": self._learn_from_interaction,
            "goal_planner": self._plan_goals,
            "context_analyzer": self._analyze_context
        }
    
    async def process_ticket_autonomously(self, ticket: CustomerTicket) -> Dict[str, Any]:
        """
        Main autonomous processing method - the agent plans and executes autonomously
        """
        print(f"🧠 Agentic AI autonomously processing ticket: {ticket.id}")
        
        # Phase 1: Autonomous Analysis and Planning
        analysis = await self._autonomous_analysis(ticket)
        
        # Phase 2: Dynamic Goal Setting
        goals = await self._set_dynamic_goals(ticket, analysis)
        
        # Phase 3: Adaptive Planning
        plan = await self._create_adaptive_plan(ticket, analysis, goals)
        
        # Phase 4: Autonomous Execution
        execution_result = await self._execute_plan_autonomously(ticket, plan)
        
        # Phase 5: Learning and Adaptation
        learning_outcome = await self._learn_and_adapt(ticket, execution_result)
        
        return {
            "ticket": ticket,
            "analysis": analysis,
            "goals": goals,
            "plan": plan,
            "execution_result": execution_result,
            "learning_outcome": learning_outcome,
            "processing_method": "autonomous",
            "agent_type": "agentic"
        }
    
    async def _autonomous_analysis(self, ticket: CustomerTicket) -> Dict[str, Any]:
        """Autonomous multi-dimensional analysis"""
        
        # Parallel analysis using multiple tools
        tasks = [
            self.tools["sentiment_analyzer"](ticket.description),
            self.tools["customer_profiler"](ticket),
            self.tools["context_analyzer"](ticket),
            self._retrieve_similar_cases(ticket)
        ]
        
        results = await asyncio.gather(*tasks)
        
        sentiment = results[0]
        customer_profile = results[1]
        context = results[2]
        similar_cases = results[3]
        
        # Advanced reasoning about the ticket
        reasoning_prompt = f"""
        As an advanced customer support AI, analyze this ticket comprehensively:
        
        Ticket: {ticket.subject}
        Description: {ticket.description}
        Customer: {ticket.customer_name}
        
        Sentiment Analysis: {sentiment}
        Customer Profile: {customer_profile}
        Context: {context}
        Similar Cases: {similar_cases}
        
        Provide a deep analysis including:
        1. Root cause analysis
        2. Customer emotional state and needs
        3. Complexity assessment
        4. Risk factors
        5. Opportunity identification
        6. Recommended approach strategy
        
        Format as JSON with clear reasoning.
        """
        
        response = await self._call_llm(reasoning_prompt, temperature=0.2)
        
        try:
            analysis = json.loads(response)
        except:
            analysis = {"raw_reasoning": response}
        
        return {
            "sentiment": sentiment,
            "customer_profile": customer_profile,
            "context": context,
            "similar_cases": similar_cases,
            "deep_analysis": analysis,
            "confidence": self._calculate_analysis_confidence(sentiment, context)
        }
    
    async def _set_dynamic_goals(self, ticket: CustomerTicket, analysis: Dict[str, Any]) -> List[Goal]:
        """Dynamically set goals based on analysis"""
        
        # AI determines what goals to pursue
        goal_setting_prompt = f"""
        Based on this analysis, determine the optimal goals for handling this customer support ticket:
        
        Analysis: {json.dumps(analysis, indent=2)}
        
        Create a prioritized list of goals with:
        1. Primary goal (customer satisfaction)
        2. Secondary goals (efficiency, learning, prevention)
        3. Success criteria for each goal
        4. Realistic timelines
        
        Consider:
        - Customer emotional state
        - Complexity of the issue
        - Available resources
        - Learning opportunities
        - Prevention of similar issues
        
        Format as JSON array of goals.
        """
        
        response = await self._call_llm(goal_setting_prompt, temperature=0.3)
        
        try:
            goal_data = json.loads(response)
            goals = []
            
            for i, g in enumerate(goal_data):
                goal = Goal(
                    objective=g.get("objective", ""),
                    priority=g.get("priority", i+1),
                    deadline=datetime.now() + timedelta(hours=g.get("hours", 24)),
                    success_criteria=g.get("success_criteria", [])
                )
                goals.append(goal)
            
            self.goals.extend(goals)
            return goals
            
        except Exception as e:
            # Fallback goals
            return [
                Goal(
                    objective="Resolve customer issue with high satisfaction",
                    priority=1,
                    deadline=datetime.now() + timedelta(hours=4),
                    success_criteria=["Issue resolved", "Customer satisfied", "Response time < 2h"]
                )
            ]
    
    async def _create_adaptive_plan(self, ticket: CustomerTicket, analysis: Dict[str, Any], goals: List[Goal]) -> List[Action]:
        """Create an adaptive execution plan"""
        
        planning_prompt = f"""
        Create a detailed action plan to achieve these goals:
        
        Goals: {[g.objective for g in goals]}
        Analysis: {json.dumps(analysis, indent=2)}
        
        Available tools: {list(self.tools.keys())}
        
        Create a sequence of actions that:
        1. Addresses the customer's immediate needs
        2. Gathers additional context if needed
        3. Provides proactive solutions
        4. Includes learning and improvement steps
        5. Has contingency options for different outcomes
        
        Each action should include:
        - Type (from: analyze, research, communicate, escalate, learn, plan, execute)
        - Description
        - Parameters
        - Expected outcome
        - Confidence level (0-1)
        
        Format as JSON array of actions.
        """
        
        response = await self._call_llm(planning_prompt, temperature=0.4)
        
        try:
            action_data = json.loads(response)
            actions = []
            
            for a in action_data:
                action = Action(
                    type=ActionType(a.get("type", "execute")),
                    description=a.get("description", ""),
                    parameters=a.get("parameters", {}),
                    confidence=a.get("confidence", 0.5),
                    expected_outcome=a.get("expected_outcome", "")
                )
                actions.append(action)
            
            return actions
            
        except Exception as e:
            # Fallback plan
            return [
                Action(
                    type=ActionType.ANALYZE,
                    description="Analyze ticket thoroughly",
                    parameters={"ticket_id": ticket.id},
                    confidence=0.8,
                    expected_outcome="Better understanding of issue"
                ),
                Action(
                    type=ActionType.COMMUNICATE,
                    description="Provide helpful response",
                    parameters={"ticket_id": ticket.id},
                    confidence=0.7,
                    expected_outcome="Customer receives helpful information"
                )
            ]
    
    async def _execute_plan_autonomously(self, ticket: CustomerTicket, plan: List[Action]) -> Dict[str, Any]:
        """Execute the plan autonomously with adaptive adjustments"""
        
        execution_log = []
        results = {}
        
        for i, action in enumerate(plan):
            print(f"🎯 Executing action {i+1}/{len(plan)}: {action.description}")
            
            try:
                # Execute the action
                if action.type == ActionType.ANALYZE:
                    result = await self._execute_analysis_action(ticket, action)
                elif action.type == ActionType.RESEARCH:
                    result = await self._execute_research_action(ticket, action)
                elif action.type == ActionType.COMMUNICATE:
                    result = await self._execute_communication_action(ticket, action)
                elif action.type == ActionType.ESCALATE:
                    result = await self._execute_escalation_action(ticket, action)
                elif action.type == ActionType.LEARN:
                    result = await self._execute_learning_action(ticket, action)
                else:
                    result = await self._execute_generic_action(ticket, action)
                
                execution_log.append({
                    "action": action,
                    "result": result,
                    "success": True,
                    "timestamp": datetime.now()
                })
                
                results[f"action_{i}"] = result
                
                # Adaptive adjustment - check if plan needs modification
                if result.get("confidence", 0) < 0.5:
                    adjustment = await self._adapt_plan_real_time(ticket, plan[i+1:], result)
                    if adjustment:
                        plan = plan[:i+1] + adjustment
                
            except Exception as e:
                execution_log.append({
                    "action": action,
                    "error": str(e),
                    "success": False,
                    "timestamp": datetime.now()
                })
                
                # Autonomous error recovery
                recovery_action = await self._autonomous_error_recovery(ticket, action, str(e))
                if recovery_action:
                    plan.insert(i+1, recovery_action)
        
        # Generate final response and recommendations
        final_response = await self._generate_final_response(ticket, execution_log, results)
        
        return {
            "execution_log": execution_log,
            "results": results,
            "final_response": final_response,
            "plan_adaptations": len([log for log in execution_log if "adapted" in log.get("result", {})]),
            "success_rate": len([log for log in execution_log if log.get("success", False)]) / len(execution_log)
        }
    
    async def _learn_and_adapt(self, ticket: CustomerTicket, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from the interaction and adapt for future use"""
        
        # Store interaction in memory
        memory = Memory(
            ticket_id=ticket.id,
            customer_context={
                "name": ticket.customer_name,
                "email": ticket.email,
                "history": self._get_customer_history(ticket.email)
            },
            actions_taken=[log["action"] for log in execution_result["execution_log"]],
            outcomes=[log.get("result", {}) for log in execution_result["execution_log"]],
            lessons_learned=[],
            sentiment_analysis=execution_result["results"].get("sentiment", {})
        )
        
        self.memory_store[ticket.id] = memory
        
        # Extract learnings
        learning_prompt = f"""
        Analyze this customer support interaction and extract key learnings:
        
        Ticket: {ticket.subject}
        Execution Log: {json.dumps(execution_result["execution_log"], default=str, indent=2)}
        Success Rate: {execution_result["success_rate"]}
        
        Identify:
        1. What worked well?
        2. What could be improved?
        3. Patterns to remember for similar cases
        4. New knowledge to add to the knowledge base
        5. Process improvements
        
        Format as JSON with clear categorization.
        """
        
        learning_analysis = await self._call_llm(learning_prompt, temperature=0.3)
        
        try:
            learnings = json.loads(learning_analysis)
            
            # Update knowledge base
            if learnings.get("new_knowledge"):
                await self._update_knowledge_base(learnings["new_knowledge"])
            
            # Update learned patterns
            if learnings.get("patterns"):
                self.learned_patterns.update(learnings["patterns"])
            
            # Store lessons in memory
            memory.lessons_learned = learnings.get("lessons", [])
            
            return {
                "learnings_extracted": learnings,
                "knowledge_base_updated": bool(learnings.get("new_knowledge")),
                "patterns_learned": len(learnings.get("patterns", {})),
                "memory_stored": True
            }
            
        except Exception as e:
            return {
                "error": f"Learning extraction failed: {str(e)}",
                "raw_learning": learning_analysis
            }
    
    # Tool implementations
    async def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Advanced sentiment analysis"""
        prompt = f"""
        Analyze the sentiment of this customer message with high precision:
        
        "{text}"
        
        Provide scores (0-1) for:
        - positive: overall positivity
        - negative: overall negativity  
        - frustrated: frustration level
        - urgent: urgency level
        - satisfied: satisfaction level
        - confused: confusion level
        
        Format as JSON.
        """
        
        response = await self._call_llm(prompt, temperature=0.1)
        try:
            return json.loads(response)
        except:
            return {"positive": 0.5, "negative": 0.5, "frustrated": 0.3, "urgent": 0.4}
    
    async def _profile_customer(self, ticket: CustomerTicket) -> Dict[str, Any]:
        """Create dynamic customer profile"""
        history = self._get_customer_history(ticket.email)
        
        profile_prompt = f"""
        Create a comprehensive customer profile based on:
        
        Current ticket: {ticket.subject} - {ticket.description}
        Historical tickets: {history}
        
        Determine:
        - communication_style: (formal, casual, technical, emotional)
        - experience_level: (beginner, intermediate, advanced, expert)
        - typical_issues: [list of common issue types]
        - satisfaction_trend: (improving, stable, declining)
        - priority_customer: (true/false)
        - preferred_resolution_style: (quick_fix, detailed_explanation, escalation)
        
        Format as JSON.
        """
        
        response = await self._call_llm(profile_prompt, temperature=0.2)
        try:
            return json.loads(response)
        except:
            return {"communication_style": "formal", "experience_level": "intermediate"}
    
    async def _analyze_context(self, ticket: CustomerTicket) -> Dict[str, Any]:
        """Analyze broader context"""
        return {
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "ticket_volume": "normal",  # Would be calculated from real data
            "related_outages": [],  # Would check system status
            "seasonal_patterns": "standard"  # Would analyze historical data
        }
    
    async def _retrieve_similar_cases(self, ticket: CustomerTicket) -> List[Dict[str, Any]]:
        """Retrieve similar cases using semantic search"""
        # Generate embedding for current ticket
        ticket_text = f"{ticket.subject} {ticket.description}"
        query_embedding = self.embedding_model.encode([ticket_text])
        
        # Search vector database (simplified - would use actual chromadb query)
        # For demo, return mock similar cases
        return [
            {
                "ticket_id": "T123",
                "similarity": 0.85,
                "resolution": "Password reset link sent",
                "resolution_time": "15 minutes"
            },
            {
                "ticket_id": "T456", 
                "similarity": 0.72,
                "resolution": "Account unlock procedure",
                "resolution_time": "5 minutes"
            }
        ]
    
    def _get_customer_history(self, email: str) -> List[Dict[str, Any]]:
        """Get customer interaction history"""
        # Mock history - would query actual database
        return [
            {"date": "2024-01-10", "issue": "login problem", "resolution": "password reset", "satisfaction": 4.5},
            {"date": "2024-01-05", "issue": "billing question", "resolution": "explanation provided", "satisfaction": 4.8}
        ]
    
    async def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """Make LLM API call with error handling"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM call failed: {str(e)}"
    
    def _calculate_analysis_confidence(self, sentiment: Dict, context: Dict) -> float:
        """Calculate confidence in analysis"""
        # Simplified confidence calculation
        sentiment_clarity = abs(sentiment.get("positive", 0.5) - sentiment.get("negative", 0.5))
        context_richness = len(context) / 10.0
        return min(1.0, (sentiment_clarity + context_richness) / 2)
    
    # Action execution methods (simplified implementations)
    async def _execute_analysis_action(self, ticket: CustomerTicket, action: Action) -> Dict[str, Any]:
        return {"action_type": "analysis", "confidence": 0.8, "insights": "Deep analysis completed"}
    
    async def _execute_research_action(self, ticket: CustomerTicket, action: Action) -> Dict[str, Any]:
        return {"action_type": "research", "confidence": 0.7, "findings": "Additional context gathered"}
    
    async def _execute_communication_action(self, ticket: CustomerTicket, action: Action) -> Dict[str, Any]:
        response = await self._generate_contextual_response(ticket)
        return {"action_type": "communication", "confidence": 0.9, "response": response}
    
    async def _execute_escalation_action(self, ticket: CustomerTicket, action: Action) -> Dict[str, Any]:
        return {"action_type": "escalation", "confidence": 1.0, "escalated_to": "senior_support"}
    
    async def _execute_learning_action(self, ticket: CustomerTicket, action: Action) -> Dict[str, Any]:
        return {"action_type": "learning", "confidence": 0.8, "learned": "New pattern identified"}
    
    async def _execute_generic_action(self, ticket: CustomerTicket, action: Action) -> Dict[str, Any]:
        return {"action_type": "generic", "confidence": 0.6, "outcome": "Action completed"}
    
    async def _generate_contextual_response(self, ticket: CustomerTicket) -> str:
        """Generate highly contextual response"""
        # Get customer profile and history
        customer_memory = self.memory_store.get(ticket.id)
        
        context_prompt = f"""
        Generate a personalized, contextual response for this customer support ticket:
        
        Customer: {ticket.customer_name}
        Subject: {ticket.subject}
        Description: {ticket.description}
        
        Customer Profile: {customer_memory.customer_context if customer_memory else "New customer"}
        Previous Actions: {customer_memory.actions_taken if customer_memory else "None"}
        
        Make the response:
        1. Highly personalized and empathetic
        2. Proactive with solutions
        3. Contextually aware
        4. Professional yet warm
        5. Include next steps and timeline
        
        Maximum 200 words.
        """
        
        return await self._call_llm(context_prompt, temperature=0.4)
    
    async def _adapt_plan_real_time(self, ticket: CustomerTicket, remaining_plan: List[Action], current_result: Dict) -> Optional[List[Action]]:
        """Adapt plan in real-time based on results"""
        if current_result.get("confidence", 1.0) < 0.5:
            # Create new action to address low confidence
            recovery_action = Action(
                type=ActionType.RESEARCH,
                description="Gather additional context due to low confidence",
                parameters={"focus": "context_clarification"},
                confidence=0.7,
                expected_outcome="Improved understanding"
            )
            return [recovery_action] + remaining_plan
        return None
    
    async def _autonomous_error_recovery(self, ticket: CustomerTicket, failed_action: Action, error: str) -> Optional[Action]:
        """Autonomously create recovery action for failed action"""
        return Action(
            type=ActionType.PLAN,
            description=f"Recovery from failed action: {failed_action.description}",
            parameters={"recovery_context": error},
            confidence=0.6,
            expected_outcome="Recover from error and continue processing"
        )
    
    async def _generate_final_response(self, ticket: CustomerTicket, execution_log: List, results: Dict) -> str:
        """Generate final comprehensive response"""
        final_prompt = f"""
        Generate a final comprehensive response based on the complete analysis and actions taken:
        
        Ticket: {ticket.subject}
        Actions Taken: {len(execution_log)} autonomous actions
        Success Rate: {results.get('success_rate', 0.0)}
        
        Provide:
        1. Clear resolution or next steps
        2. Timeline for resolution
        3. Proactive recommendations
        4. Contact information for follow-up
        
        Be empathetic, professional, and thorough.
        """
        
        return await self._call_llm(final_prompt, temperature=0.3)
    
    async def _update_knowledge_base(self, new_knowledge: Dict[str, Any]) -> None:
        """Update the vector knowledge base with new learnings"""
        # Simplified implementation - would actually update ChromaDB
        print(f"📚 Knowledge base updated with: {list(new_knowledge.keys())}")
    
    def get_capabilities(self) -> List[str]:
        """Return list of agentic AI capabilities"""
        return [
            "Autonomous planning and decision-making",
            "Dynamic goal setting based on context",
            "Real-time plan adaptation",
            "Multi-tool orchestration",
            "Contextual memory and learning",
            "Emotional intelligence and empathy",
            "Proactive problem-solving",
            "Error recovery and resilience",
            "Continuous improvement through learning",
            "Complex reasoning and analysis",
            "Semantic understanding and retrieval",
            "Customer behavior prediction",
            "Autonomous workflow creation",
            "Cross-ticket pattern recognition",
            "Predictive escalation management"
        ]
    
    def get_advantages(self) -> List[str]:
        """Return advantages over traditional AI agents"""
        return [
            "Adapts to new scenarios without reprogramming",
            "Learns and improves from every interaction",
            "Handles complex, ambiguous situations",
            "Provides personalized experiences",
            "Proactively prevents issues",
            "Operates with minimal human intervention",
            "Continuously optimizes performance",
            "Maintains contextual awareness across interactions",
            "Makes autonomous decisions within defined boundaries",
            "Scales intelligence rather than just processing"
        ]

# Example usage and testing
async def demo_agentic_ai():
    """Demonstrate the agentic AI system"""
    
    # Note: In real implementation, you'd use actual API key
    agent = AgenticAI(api_key="your-openai-api-key", model_name="gpt-4")
    
    # Sample tickets (same as traditional agent for comparison)
    tickets = [
        CustomerTicket(
            id="T001",
            customer_name="John Doe",
            email="john@example.com",
            subject="Cannot login to my account",
            description="I forgot my password and cannot access my account. This is urgent!",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            category="",
            created_at="2024-01-15T10:00:00Z"
        ),
        CustomerTicket(
            id="T002",
            customer_name="Jane Smith",
            email="jane@example.com",
            subject="Billing discrepancy",
            description="I was charged twice for the same service. Need immediate refund.",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            category="",
            created_at="2024-01-15T11:00:00Z"
        )
    ]
    
    print("=" * 60)
    print("AGENTIC AI SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    for ticket in tickets:
        print(f"\n🧠 Processing ticket {ticket.id} autonomously...")
        result = await agent.process_ticket_autonomously(ticket)
        
        print(f"\nTicket ID: {ticket.id}")
        print(f"Subject: {ticket.subject}")
        print(f"Analysis Confidence: {result['analysis']['confidence']:.2f}")
        print(f"Goals Set: {len(result['goals'])}")
        print(f"Actions Planned: {len(result['plan'])}")
        print(f"Execution Success Rate: {result['execution_result']['success_rate']:.2f}")
        print(f"Learning Outcome: {result['learning_outcome'].get('patterns_learned', 0)} patterns learned")
        print(f"Final Response: {result['execution_result']['final_response'][:200]}...")
        print("-" * 40)
    
    print("\nAgentic AI Capabilities:")
    for capability in agent.get_capabilities():
        print(f"🧠 {capability}")
    
    print("\nAdvantages over Traditional AI:")
    for advantage in agent.get_advantages():
        print(f"⚡ {advantage}")

if __name__ == "__main__":
    asyncio.run(demo_agentic_ai())