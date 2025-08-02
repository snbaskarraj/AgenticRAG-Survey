"""
Traditional AI Agent Implementation
==================================

This is a traditional AI agent that follows predefined rules and workflows.
It has limited autonomy and requires explicit programming for each task.
"""

import openai
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class CustomerTicket:
    id: str
    customer_name: str
    email: str
    subject: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    category: str
    created_at: str

class TraditionalAIAgent:
    """
    Traditional AI Agent - Rule-based system with limited autonomy
    
    Characteristics:
    - Follows predefined rules and workflows
    - Limited decision-making capabilities
    - Requires explicit programming for each scenario
    - Reactive rather than proactive
    - Simple LLM integration for text processing
    """
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.knowledge_base = self._load_knowledge_base()
        self.rules = self._define_rules()
        
    def _load_knowledge_base(self) -> Dict[str, str]:
        """Predefined knowledge base - static content"""
        return {
            "password_reset": "To reset your password, go to login page and click 'Forgot Password'",
            "account_locked": "Account lockouts are automatically resolved after 30 minutes",
            "billing_issue": "For billing issues, please contact our billing department at billing@company.com",
            "technical_support": "Technical issues require escalation to our technical team",
            "product_info": "Product information can be found in our documentation at docs.company.com"
        }
    
    def _define_rules(self) -> Dict[str, callable]:
        """Predefined rules for handling different scenarios"""
        return {
            "priority_classification": self._classify_priority,
            "category_detection": self._detect_category,
            "auto_response": self._generate_auto_response,
            "escalation_check": self._check_escalation_needed
        }
    
    def process_ticket(self, ticket: CustomerTicket) -> Dict[str, any]:
        """
        Main processing method - follows a rigid workflow
        """
        print(f"🤖 Traditional AI Agent processing ticket: {ticket.id}")
        
        # Step 1: Classify priority (rule-based)
        priority = self._classify_priority(ticket.description)
        ticket.priority = priority
        
        # Step 2: Detect category (keyword matching)
        category = self._detect_category(ticket.description)
        ticket.category = category
        
        # Step 3: Generate response (template-based with LLM assistance)
        response = self._generate_auto_response(ticket)
        
        # Step 4: Check if escalation needed (rule-based)
        needs_escalation = self._check_escalation_needed(ticket)
        
        # Step 5: Update ticket status (simple logic)
        if needs_escalation:
            ticket.status = TicketStatus.IN_PROGRESS
        else:
            ticket.status = TicketStatus.RESOLVED
        
        return {
            "ticket": ticket,
            "response": response,
            "escalated": needs_escalation,
            "processing_method": "rule-based",
            "agent_type": "traditional"
        }
    
    def _classify_priority(self, description: str) -> TicketPriority:
        """Rule-based priority classification"""
        description_lower = description.lower()
        
        # Hard-coded rules
        if any(word in description_lower for word in ["urgent", "critical", "down", "outage"]):
            return TicketPriority.CRITICAL
        elif any(word in description_lower for word in ["important", "asap", "quickly"]):
            return TicketPriority.HIGH
        elif any(word in description_lower for word in ["minor", "small", "suggestion"]):
            return TicketPriority.LOW
        else:
            return TicketPriority.MEDIUM
    
    def _detect_category(self, description: str) -> str:
        """Keyword-based category detection"""
        description_lower = description.lower()
        
        # Simple keyword matching
        if any(word in description_lower for word in ["password", "login", "access"]):
            return "authentication"
        elif any(word in description_lower for word in ["billing", "payment", "invoice"]):
            return "billing"
        elif any(word in description_lower for word in ["bug", "error", "crash", "broken"]):
            return "technical"
        elif any(word in description_lower for word in ["feature", "product", "how to"]):
            return "product_info"
        else:
            return "general"
    
    def _generate_auto_response(self, ticket: CustomerTicket) -> str:
        """Generate response using templates and simple LLM assistance"""
        
        # Try to find template response first
        template_response = self.knowledge_base.get(ticket.category)
        
        if template_response:
            # Use template with minimal customization
            return f"Dear {ticket.customer_name},\n\n{template_response}\n\nBest regards,\nCustomer Support Team"
        
        # Fall back to LLM for simple response generation
        try:
            prompt = f"""
            Generate a brief customer support response for this ticket:
            Subject: {ticket.subject}
            Description: {ticket.description}
            Category: {ticket.category}
            
            Keep it professional and concise. Maximum 100 words.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            return f"Dear {ticket.customer_name},\n\n{response.choices[0].message.content}\n\nBest regards,\nCustomer Support Team"
        
        except Exception as e:
            # Fallback to generic response
            return f"Dear {ticket.customer_name},\n\nThank you for contacting us. We have received your request and will respond within 24 hours.\n\nBest regards,\nCustomer Support Team"
    
    def _check_escalation_needed(self, ticket: CustomerTicket) -> bool:
        """Simple rule-based escalation logic"""
        escalation_keywords = ["legal", "lawsuit", "manager", "supervisor", "complaint", "refund"]
        
        return (
            ticket.priority == TicketPriority.CRITICAL or
            any(keyword in ticket.description.lower() for keyword in escalation_keywords) or
            ticket.category == "technical"
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "Priority classification (rule-based)",
            "Category detection (keyword matching)",
            "Template-based responses",
            "Simple escalation rules",
            "Basic LLM integration",
            "Fixed workflow processing"
        ]
    
    def get_limitations(self) -> List[str]:
        """Return list of agent limitations"""
        return [
            "Cannot learn from new scenarios",
            "Rigid rule-based processing",
            "Limited context understanding",
            "No autonomous decision making",
            "Cannot adapt to changing requirements",
            "Requires manual rule updates",
            "No memory of previous interactions",
            "Cannot perform complex reasoning"
        ]

# Example usage and testing
def demo_traditional_agent():
    """Demonstrate the traditional AI agent"""
    
    # Note: In real implementation, you'd use actual API key
    agent = TraditionalAIAgent(api_key="your-openai-api-key")
    
    # Sample tickets
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
    print("TRADITIONAL AI AGENT DEMONSTRATION")
    print("=" * 60)
    
    for ticket in tickets:
        result = agent.process_ticket(ticket)
        
        print(f"\nTicket ID: {ticket.id}")
        print(f"Subject: {ticket.subject}")
        print(f"Classified Priority: {result['ticket'].priority.value}")
        print(f"Detected Category: {result['ticket'].category}")
        print(f"Escalated: {result['escalated']}")
        print(f"Status: {result['ticket'].status.value}")
        print(f"Response: {result['response']}")
        print("-" * 40)
    
    print("\nAgent Capabilities:")
    for capability in agent.get_capabilities():
        print(f"✓ {capability}")
    
    print("\nAgent Limitations:")
    for limitation in agent.get_limitations():
        print(f"✗ {limitation}")

if __name__ == "__main__":
    demo_traditional_agent()