class CancellationService:
    def __init__(self):
        # Common cancellation methods by service
        self.cancellation_info = {
            'netflix': {
                'methods': ['Online Form', 'Phone'],
                'url': 'https://www.netflix.com/cancelplan',
                'phone': '1-866-579-7172'
            },
            'spotify': {
                'methods': ['Online Form'],
                'url': 'https://www.spotify.com/account/subscription/cancel/'
            },
            'hulu': {
                'methods': ['Online Form'],
                'url': 'https://secure.hulu.com/account/cancel'
            },
            'amazon prime': {
                'methods': ['Online Form'],
                'url': 'https://www.amazon.com/gp/primecentral'
            },
            # Add more services as needed
        }
        
        # Email templates
        self.templates = {
            'Standard Cancellation': """Subject: Subscription Cancellation Request - [Account Number]

Dear [Company] Support Team,

I am writing to request the cancellation of my subscription, effective immediately.

Account Information:
- Name: [Your Name]
- Email: [Your Email]
- Account/Subscription Number: [Account Number]
- Billing Address: [Your Address]

Please confirm receipt of this cancellation request and provide any necessary information regarding the cancellation process. If there are any final charges or refunds, please detail them in your response.

Thank you for your assistance.

Sincerely,
[Your Name]""",
            
            'Request Refund': """Subject: Subscription Cancellation and Refund Request - [Account Number]

Dear [Company] Support Team,

I am writing to request the cancellation of my subscription and a refund for [specify reason: e.g., unused portion, service issues].

Account Information:
- Name: [Your Name]
- Email: [Your Email]
- Account/Subscription Number: [Account Number]
- Billing Address: [Your Address]

Reason for Cancellation and Refund Request:
[Clearly explain your reason for requesting a refund]

I would appreciate a refund of [amount] to be processed back to my original payment method. Please confirm receipt of this request and provide information on the expected timeline for processing.

Thank you for your understanding and assistance.

Sincerely,
[Your Name]""",
            
            'Pause Subscription': """Subject: Request to Pause Subscription - [Account Number]

Dear [Company] Support Team,

I am writing to request a temporary pause of my subscription.

Account Information:
- Name: [Your Name]
- Email: [Your Email]
- Account/Subscription Number: [Account Number]

I would like to pause my subscription from [start date] to [end date]. Please confirm if this is possible and if there are any fees or special procedures associated with pausing rather than canceling.

Thank you for your assistance.

Sincerely,
[Your Name]""",
            
            'Negotiate Better Rate': """Subject: Subscription Rate Review Request - [Account Number]

Dear [Company] Support Team,

I have been a loyal customer of [Company] for [time period], and I'm writing to inquire about available options for reducing my subscription rate.

Account Information:
- Name: [Your Name]
- Email: [Your Email]
- Account/Subscription Number: [Account Number]
- Current Plan: [Plan Details]
- Current Rate: [Current Rate]

I've noticed that [mention competitor offers or new customer rates if applicable]. Due to [budget constraints/changes in usage needs], I'm considering canceling my subscription, but I would prefer to remain a customer if we can find a more suitable rate.

Are there any loyalty discounts, annual payment options, or alternative plans that could help reduce my costs while maintaining the service?

I appreciate your consideration and look forward to your response.

Sincerely,
[Your Name]"""
        }
    
    def get_cancellation_methods(self, subscription_name):
        """Get available cancellation methods for a subscription"""
        # Check if we have specific info for this subscription
        for service, info in self.cancellation_info.items():
            if service in subscription_name.lower():
                return info['methods']
        
        # Default methods if not found
        return ['Email', 'Phone', 'Online Form']
    
    def generate_email_template(self, subscription_name):
        """Generate an email template for cancellation"""
        template = self.templates['Standard Cancellation']
        
        # Replace company name in template
        template = template.replace('[Company]', subscription_name)
        
        return template
    
    def generate_phone_script(self, subscription_name):
        """Generate a phone script for cancellation"""
        script = f"""Cancellation Phone Script for {subscription_name}

1. Call the customer service number
   - For {subscription_name}: {self.get_phone_number(subscription_name)}

2. Navigate the phone menu
   - Select options for 'account management' or 'cancellation'

3. When speaking with a representative:
   - "Hello, I'd like to cancel my {subscription_name} subscription."
   - Provide your account information when requested
   - Be polite but firm about your decision to cancel
   - If asked why: "I'm streamlining my subscriptions" or "It no longer fits my needs"
   - Decline offers to stay unless they're genuinely better

4. Confirmation
   - Ask for a cancellation confirmation number or email
   - Note the name of the representative you spoke with
   - Confirm the effective date of cancellation

5. Follow-up
   - Check your email for cancellation confirmation
   - Monitor your account to ensure no further charges"""
        
        return script
    
    def get_cancellation_url(self, subscription_name):
        """Get the cancellation URL for a subscription"""
        # Check if we have specific info for this subscription
        for service, info in self.cancellation_info.items():
            if service in subscription_name.lower() and 'url' in info:
                return info['url']
        
        # Default if not found
        return f"https://www.google.com/search?q=how+to+cancel+{subscription_name.replace(' ', '+')}+subscription"
    
    def get_phone_number(self, subscription_name):
        """Get the customer service phone number for a subscription"""
        # Check if we have specific info for this subscription
        for service, info in self.cancellation_info.items():
            if service in subscription_name.lower() and 'phone' in info:
                return info['phone']
        
        # Default if not found
        return "Check the company's website for customer service contact information"
    
    def get_template(self, template_type):
        """Get a specific email template"""
        if template_type in self.templates:
            return self.templates[template_type]
        else:
            return self.templates['Standard Cancellation']