import React from 'react'

const APISection: React.FC = () => {
  return (
    <section id="api" className="py-32 minimal-gradient relative z-10">
      <div className="max-w-6xl mx-auto px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8">
            <div className="space-y-6">
              <h2 className="text-4xl md:text-5xl font-bold text-white">Developer API</h2>
              <p className="text-xl text-charcoal-300 font-light leading-relaxed">
                Integrate AI detection into your applications with our RESTful API. Built for scale with enterprise-grade security.
              </p>
            </div>
            
            <div className="space-y-6">
              {[
                "RESTful endpoints for all content types",
                "JWT authentication & RBAC",
                "Async processing with webhooks",
                "Rate limiting & usage analytics"
              ].map((item, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="w-1.5 h-1.5 bg-white rounded-full mt-3 flex-shrink-0"></div>
                  <span className="text-charcoal-300">{item}</span>
                </div>
              ))}
            </div>
            
            <button className="bg-white text-black px-8 py-4 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold hover-lift">
              View API Docs
            </button>
          </div>
          
          <div>
            <div className="bg-charcoal-900 rounded-2xl p-8 border border-charcoal-800">
              <div className="flex items-center justify-between mb-6">
                <span className="text-sm text-charcoal-400 font-mono">POST /api/v1/analyze/text</span>
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
              </div>
              <pre className="text-sm text-charcoal-200 overflow-x-auto font-mono leading-relaxed"><code>{
`{
  "content": "Your text content here...",
  "options": {
    "model": "advanced",
    "confidence_threshold": 0.8
  }
}`}
</code></pre>
              <div className="mt-6 pt-6 border-t border-charcoal-700">
                <span className="text-sm text-charcoal-400 font-mono">Response:</span>
                <pre className="text-sm text-green-400 mt-3 font-mono leading-relaxed"><code>{
`{
  "ai_probability": 0.87,
  "confidence": "high",
  "model_version": "v2.1",
  "processing_time": "1.2s"
}`}
</code></pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default APISection