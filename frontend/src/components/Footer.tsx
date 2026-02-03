import { HeartIcon } from '@heroicons/react/24/solid'

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-sydney-500 flex items-center justify-center text-white font-bold text-sm">
              S
            </div>
            <span className="text-lg font-semibold gradient-text">Sydney Events</span>
          </div>
          
          <p className="text-sm text-gray-500 flex items-center gap-1">
            Made with <HeartIcon className="w-4 h-4 text-red-500" /> for Sydney
          </p>
          
          <p className="text-sm text-gray-400">
            © {new Date().getFullYear()} Sydney Events. All rights reserved.
          </p>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-100">
          <p className="text-xs text-center text-gray-400">
            Events are automatically scraped from public sources. We are not affiliated with any event organizers.
            <br />
            Always verify event details on the official source before attending.
          </p>
        </div>
      </div>
    </footer>
  )
}
