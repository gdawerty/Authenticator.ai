import { motion } from 'framer-motion'

export function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-black/10">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Brand */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#6f8f88] flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="font-semibold">Authentia AI</span>
          </div>

          {/* Links */}
          <div className="flex items-center gap-8 text-sm text-[#2a2a2a]/60">
            <a href="#" className="hover:text-[#6f8f88] transition-colors">Privacy</a>
            <a href="#" className="hover:text-[#6f8f88] transition-colors">Terms</a>
            <a href="#" className="hover:text-[#6f8f88] transition-colors">Security</a>
          </div>

          {/* Status */}
          <div className="flex items-center gap-2 text-sm text-[#2a2a2a]/50">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>All systems operational</span>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-black/10 text-center text-sm text-[#2a2a2a]/50">
          {new Date().getFullYear()} Authentia AI. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
