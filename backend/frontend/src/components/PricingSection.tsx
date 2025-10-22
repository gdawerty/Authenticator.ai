import React from 'react'

const PricingSection: React.FC = () => {
  const plans = [
    {
      name: "Starter",
      price: "$29",
      period: "/month",
      popular: false,
      features: [
        "1,000 API calls/month",
        "All content types",
        "Email support"
      ],
      buttonText: "Get Started",
      buttonVariant: "outline"
    },
    {
      name: "Professional",
      price: "$99",
      period: "/month",
      popular: true,
      features: [
        "10,000 API calls/month",
        "Priority processing",
        "Webhooks & analytics",
        "24/7 support"
      ],
      buttonText: "Get Started",
      buttonVariant: "primary"
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      popular: false,
      features: [
        "Unlimited API calls",
        "Custom models",
        "On-premise deployment",
        "Dedicated support"
      ],
      buttonText: "Contact Sales",
      buttonVariant: "outline"
    }
  ]

  return (
    <section id="pricing" className="py-32 relative z-10" style={{ background: 'linear-gradient(180deg, #1a1a1a 0%, #222222 100%)' }}>
      <div className="max-w-6xl mx-auto px-8">
        <div className="text-center mb-24">
          <h2 className="text-4xl md:text-5xl font-bold mb-8 text-white">Transparent Pricing</h2>
          <p className="text-xl text-charcoal-300 max-w-2xl mx-auto font-light">
            Choose the plan that fits your needs. All plans include core detection capabilities.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div 
              key={index}
              className={`glass-minimal p-10 rounded-2xl hover-lift relative ${plan.popular ? 'border border-white/20' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-white text-black px-6 py-2 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
              )}
              <div className="space-y-8">
                <div className="space-y-4">
                  <h3 className="text-2xl font-semibold text-white">{plan.name}</h3>
                  <div>
                    <span className="text-5xl font-bold text-white">{plan.price}</span>
                    {plan.period && <span className="text-charcoal-400 text-lg">{plan.period}</span>}
                  </div>
                </div>
                
                <div className="space-y-4">
                  {plan.features.map((feature, i) => (
                    <div key={i} className="flex items-start space-x-3">
                      <div className="w-1.5 h-1.5 bg-white rounded-full mt-3 flex-shrink-0"></div>
                      <span className="text-charcoal-300">{feature}</span>
                    </div>
                  ))}
                </div>
                
                <button 
                  className={`w-full py-4 rounded-lg transition-all duration-300 font-semibold hover-lift ${
                    plan.buttonVariant === 'primary' 
                      ? 'bg-white text-black hover:bg-charcoal-100' 
                      : 'border border-charcoal-600 text-white hover:border-white hover:bg-white hover:text-black'
                  }`}
                >
                  {plan.buttonText}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PricingSection