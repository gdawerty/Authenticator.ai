import React from 'react'

const ContactSection: React.FC = () => {
  const handleContactForm = (e: React.FormEvent) => {
    e.preventDefault()
    alert("Thank you for your message! We'll get back to you within 24 hours.")
    const form = e.target as HTMLFormElement
    form.reset()
  }

  const contactMethods = [
    {
      title: "Email Us",
      icon: (
        <svg className="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
        </svg>
      ),
      details: ["hello@authentia.com", "enterprise@authentia.com"]
    },
    {
      title: "Live Chat",
      icon: (
        <svg className="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
        </svg>
      ),
      details: ["Available 24/7 for enterprise customers", "9 AM - 6 PM PST for all others"]
    },
    {
      title: "SLA Guarantee",
      icon: (
        <svg className="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      ),
      details: ["99.9% uptime guarantee", "Enterprise support SLA available"]
    }
  ]

  return (
    <section className="py-32 minimal-gradient relative z-10">
      <div className="max-w-4xl mx-auto px-8">
        <div className="text-center mb-24">
          <h2 className="text-4xl md:text-5xl font-bold mb-8 text-white">Get In Touch</h2>
          <p className="text-xl text-charcoal-300 font-light">
            Ready to integrate AI detection into your workflow? Let's talk.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-16">
          <div className="space-y-12">
            {contactMethods.map((method, index) => (
              <div key={index} className="flex items-start space-x-6">
                <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center flex-shrink-0">
                  {method.icon}
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-semibold text-white">{method.title}</h3>
                  {method.details.map((detail, i) => (
                    <p key={i} className="text-charcoal-300">{detail}</p>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <div>
            <form className="space-y-6" onSubmit={handleContactForm}>
              <div>
                <input 
                  type="text" 
                  placeholder="Your Name" 
                  required 
                  className="w-full bg-charcoal-800 text-white p-6 rounded-lg border border-charcoal-700 focus:border-charcoal-500 focus:outline-none transition-colors duration-300"
                />
              </div>
              <div>
                <input 
                  type="email" 
                  placeholder="Your Email" 
                  required 
                  className="w-full bg-charcoal-800 text-white p-6 rounded-lg border border-charcoal-700 focus:border-charcoal-500 focus:outline-none transition-colors duration-300"
                />
              </div>
              <div>
                <select className="w-full bg-charcoal-800 text-white p-6 rounded-lg border border-charcoal-700 focus:border-charcoal-500 focus:outline-none transition-colors duration-300">
                  <option>General Inquiry</option>
                  <option>Enterprise Sales</option>
                  <option>Technical Support</option>
                  <option>Partnership</option>
                </select>
              </div>
              <div>
                <textarea 
                  placeholder="Your Message" 
                  rows={4} 
                  required 
                  className="w-full bg-charcoal-800 text-white p-6 rounded-lg border border-charcoal-700 focus:border-charcoal-500 focus:outline-none resize-none transition-colors duration-300"
                ></textarea>
              </div>
              <button 
                type="submit" 
                className="w-full bg-white text-black py-4 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold hover-lift"
              >
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  )
}

export default ContactSection