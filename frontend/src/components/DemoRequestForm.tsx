import React, { useState } from 'react';

interface DemoRequestFormProps {
  onBack?: () => void;
}

const DemoRequestForm: React.FC<DemoRequestFormProps> = ({ onBack }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    companyName: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Demo request submitted:', formData);
    setSubmitted(true);
    // Here you would typically send the data to your backend
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-[#C8C8BF] flex items-center justify-center px-6">
        <div className="max-w-2xl mx-auto text-center">
          <div className="bg-[#6F8F88] w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-[#2a2a2a] mb-4">
            Thank you for your interest!
          </h1>
          <p className="text-xl text-[#2a2a2a]/70 mb-8">
            We've received your demo request and will get back to you shortly.
          </p>
          <button
            onClick={onBack}
            className="bg-[#6F8F88] text-white px-8 py-3 rounded-lg font-medium hover:shadow-lg hover:shadow-[#6F8F88]/50 transition-all duration-300"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#C8C8BF] flex items-center justify-center px-6 py-20">
      <div className="w-full max-w-2xl">
        {/* Back Button */}
        <button
          onClick={onBack}
          className="mb-6 text-[#2a2a2a]/70 hover:text-[#2a2a2a] transition-colors duration-200 flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          <span>Back to Home</span>
        </button>

        {/* Form Container */}
        <div className="bg-[#C8C8BF] border-2 border-[#6F8F88]/30 rounded-2xl p-8 shadow-xl">
          <h1 className="text-4xl font-bold text-[#2a2a2a] mb-2 text-center">
            Request a Demo
          </h1>
          <p className="text-[#2a2a2a]/70 mb-8 text-center">
            Fill out the form below and we'll get in touch with you soon
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* First Name & Last Name */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-[#2a2a2a] mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20 transition-all"
                  placeholder="John"
                />
              </div>
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-[#2a2a2a] mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20 transition-all"
                  placeholder="Doe"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-[#2a2a2a] mb-2">
                Email Address *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20 transition-all"
                placeholder="john.doe@company.com"
              />
            </div>

            {/* Company Name */}
            <div>
              <label htmlFor="companyName" className="block text-sm font-medium text-[#2a2a2a] mb-2">
                Company Name *
              </label>
              <input
                type="text"
                id="companyName"
                name="companyName"
                value={formData.companyName}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20 transition-all"
                placeholder="Your Company Inc."
              />
            </div>

            {/* Message */}
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-[#2a2a2a] mb-2">
                Message
              </label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows={5}
                className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20 transition-all resize-none"
                placeholder="Tell us about your needs..."
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full bg-[#6F8F88] text-white py-4 rounded-lg font-medium text-lg hover:shadow-lg hover:shadow-[#6F8F88]/50 transition-all duration-300 hover:-translate-y-0.5"
            >
              Submit Request
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default DemoRequestForm;
