import { useState, useEffect, useCallback } from 'react'
import { Event, EventFilter } from '../types'
import { eventsApi } from '../api'
import EventCard from '../components/EventCard'
import TicketModal from '../components/TicketModal'
import { 
  MagnifyingGlassIcon, 
  FunnelIcon, 
  SparklesIcon,
  CalendarDaysIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'

export default function HomePage() {
  const [events, setEvents] = useState<Event[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [sources, setSources] = useState<string[]>([])
  
  // Filters
  const [filters, setFilters] = useState<EventFilter>({
    city: 'Sydney',
    page: 1,
    per_page: 12,
  })
  const [showFilters, setShowFilters] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)

  const fetchEvents = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await eventsApi.getEvents(filters)
      setEvents(response.events)
      setTotalPages(response.total_pages)
      setTotal(response.total)
    } catch (error) {
      console.error('Failed to fetch events:', error)
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  const fetchSources = async () => {
    try {
      const sourcesData = await eventsApi.getSources()
      setSources(sourcesData)
    } catch (error) {
      console.error('Failed to fetch sources:', error)
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [fetchEvents])

  useEffect(() => {
    fetchSources()
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setFilters(prev => ({ ...prev, keyword: searchQuery, page: 1 }))
  }

  const handleGetTickets = (event: Event) => {
    setSelectedEvent(event)
    setIsModalOpen(true)
  }

  const clearFilters = () => {
    setFilters({ city: 'Sydney', page: 1, per_page: 12 })
    setSearchQuery('')
  }

  const hasActiveFilters = filters.keyword || filters.status || filters.source || filters.date_from

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-sydney-700 py-16 lg:py-24">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        <div className="absolute inset-0 bg-gradient-to-t from-primary-800/50 to-transparent" />
        
        {/* Floating elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-sydney-400/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-primary-400/20 rounded-full blur-3xl animate-pulse-slow" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm text-white/90 text-sm font-medium mb-6">
                <SparklesIcon className="w-4 h-4" />
                Discover amazing events in Sydney
              </span>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
                What's happening in{' '}
                <span className="text-sydney-300">Sydney</span>?
              </h1>
              
              <p className="text-lg sm:text-xl text-white/80 max-w-2xl mx-auto mb-10">
                Find concerts, festivals, exhibitions, and more. 
                Automatically curated from the best event sources.
              </p>
            </motion.div>

            {/* Search Bar */}
            <motion.form
              onSubmit={handleSearch}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="max-w-2xl mx-auto"
            >
              <div className="relative flex gap-2">
                <div className="relative flex-1">
                  <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search events, venues, or keywords..."
                    className="w-full pl-12 pr-4 py-4 rounded-xl bg-white shadow-2xl shadow-black/20 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-white/30"
                  />
                </div>
                <button
                  type="submit"
                  className="px-8 py-4 bg-white text-primary-600 font-semibold rounded-xl shadow-2xl shadow-black/20 hover:bg-gray-50 transition-colors"
                >
                  Search
                </button>
              </div>
            </motion.form>
          </div>
        </div>
      </section>

      {/* Events Section */}
      <section className="py-12 lg:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Filters Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                <CalendarDaysIcon className="w-7 h-7 inline-block mr-2 text-primary-500" />
                Upcoming Events
              </h2>
              <p className="text-gray-500 mt-1">
                {total} events found {filters.keyword && `for "${filters.keyword}"`}
              </p>
            </div>

            <div className="flex items-center gap-3">
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="flex items-center gap-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <XMarkIcon className="w-4 h-4" />
                  Clear filters
                </button>
              )}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={clsx(
                  'btn-secondary text-sm',
                  showFilters && 'bg-gray-100'
                )}
              >
                <FunnelIcon className="w-5 h-5 mr-2" />
                Filters
              </button>
            </div>
          </div>

          {/* Filters Panel */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="card p-6 mb-8">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Status Filter */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Status
                      </label>
                      <select
                        value={filters.status || ''}
                        onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value || undefined, page: 1 }))}
                        className="input"
                      >
                        <option value="">All statuses</option>
                        <option value="new">New</option>
                        <option value="updated">Updated</option>
                        <option value="inactive">Inactive</option>
                        <option value="imported">Imported</option>
                      </select>
                    </div>

                    {/* Source Filter */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Source
                      </label>
                      <select
                        value={filters.source || ''}
                        onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value || undefined, page: 1 }))}
                        className="input"
                      >
                        <option value="">All sources</option>
                        {sources.map(source => (
                          <option key={source} value={source}>{source}</option>
                        ))}
                      </select>
                    </div>

                    {/* Date From */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        From Date
                      </label>
                      <input
                        type="date"
                        value={filters.date_from || ''}
                        onChange={(e) => setFilters(prev => ({ ...prev, date_from: e.target.value || undefined, page: 1 }))}
                        className="input"
                      />
                    </div>

                    {/* Date To */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        To Date
                      </label>
                      <input
                        type="date"
                        value={filters.date_to || ''}
                        onChange={(e) => setFilters(prev => ({ ...prev, date_to: e.target.value || undefined, page: 1 }))}
                        className="input"
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Events Grid */}
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="card animate-pulse">
                  <div className="h-48 bg-gray-200 rounded-t-2xl" />
                  <div className="p-5 space-y-3">
                    <div className="h-6 bg-gray-200 rounded w-3/4" />
                    <div className="h-4 bg-gray-200 rounded w-1/2" />
                    <div className="h-4 bg-gray-200 rounded w-2/3" />
                    <div className="h-10 bg-gray-200 rounded-xl mt-4" />
                  </div>
                </div>
              ))}
            </div>
          ) : events.length === 0 ? (
            <div className="text-center py-16">
              <CalendarDaysIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No events found</h3>
              <p className="text-gray-500 mb-6">
                Try adjusting your filters or search query.
              </p>
              <button onClick={clearFilters} className="btn-primary">
                Clear all filters
              </button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {events.map((event) => (
                  <EventCard
                    key={event.id}
                    event={event}
                    onGetTickets={handleGetTickets}
                  />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-12">
                  <button
                    onClick={() => setFilters(prev => ({ ...prev, page: Math.max(1, (prev.page || 1) - 1) }))}
                    disabled={filters.page === 1}
                    className="btn-secondary disabled:opacity-50"
                  >
                    Previous
                  </button>
                  
                  <span className="px-4 py-2 text-sm text-gray-600">
                    Page {filters.page} of {totalPages}
                  </span>
                  
                  <button
                    onClick={() => setFilters(prev => ({ ...prev, page: Math.min(totalPages, (prev.page || 1) + 1) }))}
                    disabled={filters.page === totalPages}
                    className="btn-secondary disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      {/* Ticket Modal */}
      <TicketModal
        event={selectedEvent}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  )
}
