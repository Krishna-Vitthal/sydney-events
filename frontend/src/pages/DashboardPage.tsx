import { useState, useEffect, useCallback, Fragment } from 'react'
import { Event, EventFilter, DashboardStats } from '../types'
import { eventsApi, scraperApi } from '../api'
import { useAuthStore } from '../store/authStore'
import { format, parseISO } from 'date-fns'
import { Dialog, Transition } from '@headlessui/react'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import {
  MagnifyingGlassIcon,
  ChartBarIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XMarkIcon,
  CalendarDaysIcon,
  MapPinIcon,
  LinkIcon,
  DocumentTextIcon,
  PlusIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'

export default function DashboardPage() {
  const { isAuthenticated, isLoading: authLoading, login } = useAuthStore()
  
  const [events, setEvents] = useState<Event[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [sources, setSources] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isScrapingRunning, setIsScrapingRunning] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [importNotes, setImportNotes] = useState('')
  const [showImportDialog, setShowImportDialog] = useState(false)
  const [eventToImport, setEventToImport] = useState<Event | null>(null)
  
  // Filters
  const [filters, setFilters] = useState<EventFilter>({
    city: 'Sydney',
    page: 1,
    per_page: 50,
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [totalPages, setTotalPages] = useState(1)

  const fetchData = useCallback(async () => {
    if (!isAuthenticated) return
    
    setIsLoading(true)
    try {
      const [eventsRes, statsRes, sourcesRes] = await Promise.all([
        eventsApi.getEvents(filters),
        eventsApi.getStats(),
        eventsApi.getSources(),
      ])
      setEvents(eventsRes.events)
      setTotalPages(eventsRes.total_pages)
      setStats(statsRes)
      setSources(sourcesRes)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }, [filters, isAuthenticated])

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      // Show login prompt instead of redirecting
      return
    }
    fetchData()
  }, [fetchData, isAuthenticated, authLoading])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setFilters(prev => ({ ...prev, keyword: searchQuery, page: 1 }))
  }

  const handleRunScraper = async () => {
    setIsScrapingRunning(true)
    try {
      const result = await scraperApi.runScrapers()
      toast.success(`Scraping complete! Found ${result.results.total_found} events (${result.results.new} new, ${result.results.updated} updated)`)
      fetchData()
    } catch (error) {
      toast.error('Failed to run scrapers')
    } finally {
      setIsScrapingRunning(false)
    }
  }

  const handleImportEvent = async () => {
    if (!eventToImport) return
    
    try {
      await eventsApi.importEvent(eventToImport.id, importNotes)
      toast.success('Event imported successfully!')
      setShowImportDialog(false)
      setEventToImport(null)
      setImportNotes('')
      fetchData()
      
      // Update selected event if it's the imported one
      if (selectedEvent?.id === eventToImport.id) {
        setSelectedEvent(prev => prev ? { ...prev, is_imported: true, status: 'imported' } : null)
      }
    } catch (error) {
      toast.error('Failed to import event')
    }
  }

  const handleUnimportEvent = async (eventId: number) => {
    try {
      await eventsApi.unimportEvent(eventId)
      toast.success('Import removed')
      fetchData()
      
      if (selectedEvent?.id === eventId) {
        setSelectedEvent(prev => prev ? { ...prev, is_imported: false, status: 'updated' } : null)
      }
    } catch (error) {
      toast.error('Failed to remove import')
    }
  }

  const formatDate = (dateStr: string | null, fallback?: string) => {
    if (!dateStr) return fallback || 'Date TBA'
    try {
      return format(parseISO(dateStr), 'MMM d, yyyy h:mm a')
    } catch {
      return fallback || dateStr
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { class: string; label: string; icon: typeof SparklesIcon }> = {
      new: { class: 'badge-new', label: 'New', icon: SparklesIcon },
      updated: { class: 'badge-updated', label: 'Updated', icon: ArrowPathIcon },
      inactive: { class: 'badge-inactive', label: 'Inactive', icon: ExclamationTriangleIcon },
      imported: { class: 'badge-imported', label: 'Imported', icon: CheckCircleIcon },
    }
    return badges[status] || badges.new
  }

  // Show login prompt if not authenticated
  if (authLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-sydney-500 flex items-center justify-center text-white text-3xl font-bold mx-auto mb-6 shadow-lg">
            <ChartBarIcon className="w-10 h-10" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            Dashboard Access Required
          </h1>
          <p className="text-gray-500 mb-6">
            Sign in with your Google account to access the admin dashboard and manage events.
          </p>
          <button onClick={login} className="btn-primary">
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Sign in with Google
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              Dashboard
            </h1>
            <p className="text-gray-500 mt-1">Manage and review scraped events</p>
          </div>
          
          <button
            onClick={handleRunScraper}
            disabled={isScrapingRunning}
            className="btn-primary disabled:opacity-50"
          >
            <ArrowPathIcon className={clsx('w-5 h-5 mr-2', isScrapingRunning && 'animate-spin')} />
            {isScrapingRunning ? 'Scraping...' : 'Run Scrapers'}
          </button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            <div className="card p-4">
              <p className="text-sm text-gray-500">Total Events</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_events}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-500">New</p>
              <p className="text-2xl font-bold text-green-600">{stats.new_events}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-500">Updated</p>
              <p className="text-2xl font-bold text-blue-600">{stats.updated_events}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-500">Inactive</p>
              <p className="text-2xl font-bold text-gray-400">{stats.inactive_events}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-500">Imported</p>
              <p className="text-2xl font-bold text-purple-600">{stats.imported_events}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-500">Leads</p>
              <p className="text-2xl font-bold text-primary-600">{stats.total_leads}</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Left Panel - Table */}
          <div className="flex-1">
            <div className="card">
              {/* Filters */}
              <div className="p-4 border-b border-gray-100">
                <div className="flex flex-col sm:flex-row gap-4">
                  <form onSubmit={handleSearch} className="flex-1">
                    <div className="relative">
                      <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search events..."
                        className="input pl-10"
                      />
                    </div>
                  </form>
                  
                  <div className="flex gap-2">
                    <select
                      value={filters.status || ''}
                      onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value || undefined, page: 1 }))}
                      className="input w-auto"
                    >
                      <option value="">All Status</option>
                      <option value="new">New</option>
                      <option value="updated">Updated</option>
                      <option value="inactive">Inactive</option>
                      <option value="imported">Imported</option>
                    </select>
                    
                    <select
                      value={filters.source || ''}
                      onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value || undefined, page: 1 }))}
                      className="input w-auto"
                    >
                      <option value="">All Sources</option>
                      {sources.map(source => (
                        <option key={source} value={source}>{source}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                {isLoading ? (
                  <div className="p-8 text-center">
                    <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto" />
                  </div>
                ) : events.length === 0 ? (
                  <div className="p-8 text-center">
                    <CalendarDaysIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">No events found</p>
                  </div>
                ) : (
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="text-left px-4 py-3 text-sm font-semibold text-gray-600">Event</th>
                        <th className="text-left px-4 py-3 text-sm font-semibold text-gray-600">Date</th>
                        <th className="text-left px-4 py-3 text-sm font-semibold text-gray-600">Source</th>
                        <th className="text-left px-4 py-3 text-sm font-semibold text-gray-600">Status</th>
                        <th className="text-center px-4 py-3 text-sm font-semibold text-gray-600">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {events.map((event) => {
                        const badge = getStatusBadge(event.status)
                        const BadgeIcon = badge.icon
                        return (
                          <tr
                            key={event.id}
                            onClick={() => setSelectedEvent(event)}
                            className={clsx(
                              'cursor-pointer hover:bg-gray-50 transition-colors',
                              selectedEvent?.id === event.id && 'bg-primary-50'
                            )}
                          >
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-3">
                                {event.image_url ? (
                                  <img
                                    src={event.image_url}
                                    alt=""
                                    className="w-10 h-10 rounded-lg object-cover bg-gray-100"
                                    onError={(e) => {
                                      (e.target as HTMLImageElement).style.display = 'none'
                                    }}
                                  />
                                ) : (
                                  <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                                    <CalendarDaysIcon className="w-5 h-5 text-gray-400" />
                                  </div>
                                )}
                                <div>
                                  <p className="font-medium text-gray-900 line-clamp-1 max-w-xs">
                                    {event.title}
                                  </p>
                                  {event.venue_name && (
                                    <p className="text-xs text-gray-500 line-clamp-1">
                                      {event.venue_name}
                                    </p>
                                  )}
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600">
                              {formatDate(event.date_time, event.date_string || undefined)}
                            </td>
                            <td className="px-4 py-3">
                              <span className="text-sm text-gray-600">{event.source_name}</span>
                            </td>
                            <td className="px-4 py-3">
                              <span className={clsx('badge inline-flex items-center gap-1', badge.class)}>
                                <BadgeIcon className="w-3 h-3" />
                                {badge.label}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              {event.is_imported ? (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleUnimportEvent(event.id)
                                  }}
                                  className="text-sm text-red-600 hover:text-red-700 font-medium"
                                >
                                  Remove
                                </button>
                              ) : (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    setEventToImport(event)
                                    setShowImportDialog(true)
                                  }}
                                  className="btn-primary text-xs py-1 px-3"
                                >
                                  <PlusIcon className="w-4 h-4 mr-1" />
                                  Import
                                </button>
                              )}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                )}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
                  <button
                    onClick={() => setFilters(prev => ({ ...prev, page: Math.max(1, (prev.page || 1) - 1) }))}
                    disabled={filters.page === 1}
                    className="btn-secondary text-sm disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-500">
                    Page {filters.page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setFilters(prev => ({ ...prev, page: Math.min(totalPages, (prev.page || 1) + 1) }))}
                    disabled={filters.page === totalPages}
                    className="btn-secondary text-sm disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Preview */}
          <div className="lg:w-[400px] xl:w-[450px]">
            <div className="card sticky top-24">
              <AnimatePresence mode="wait">
                {selectedEvent ? (
                  <motion.div
                    key={selectedEvent.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="divide-y divide-gray-100"
                  >
                    {/* Image */}
                    {selectedEvent.image_url && (
                      <div className="aspect-video overflow-hidden rounded-t-2xl bg-gray-100">
                        <img
                          src={selectedEvent.image_url}
                          alt={selectedEvent.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                    
                    {/* Content */}
                    <div className="p-5">
                      <div className="flex items-start justify-between gap-3 mb-4">
                        <h3 className="text-lg font-bold text-gray-900">
                          {selectedEvent.title}
                        </h3>
                        <span className={clsx('badge flex-shrink-0', getStatusBadge(selectedEvent.status).class)}>
                          {getStatusBadge(selectedEvent.status).label}
                        </span>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="flex items-start gap-3">
                          <CalendarDaysIcon className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-medium text-gray-900">
                              {formatDate(selectedEvent.date_time, selectedEvent.date_string || undefined)}
                            </p>
                            <p className="text-xs text-gray-500">Event Date</p>
                          </div>
                        </div>
                        
                        {selectedEvent.venue_name && (
                          <div className="flex items-start gap-3">
                            <MapPinIcon className="w-5 h-5 text-sydney-500 flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="font-medium text-gray-900">{selectedEvent.venue_name}</p>
                              {selectedEvent.venue_address && (
                                <p className="text-xs text-gray-500">{selectedEvent.venue_address}</p>
                              )}
                            </div>
                          </div>
                        )}
                        
                        <div className="flex items-start gap-3">
                          <LinkIcon className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-medium text-gray-900">{selectedEvent.source_name}</p>
                            <a
                              href={selectedEvent.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-primary-600 hover:text-primary-700 inline-flex items-center gap-1"
                            >
                              View original
                              <ArrowTopRightOnSquareIcon className="w-3 h-3" />
                            </a>
                          </div>
                        </div>
                      </div>
                      
                      {selectedEvent.description && (
                        <div className="mt-4 pt-4 border-t border-gray-100">
                          <div className="flex items-center gap-2 mb-2">
                            <DocumentTextIcon className="w-4 h-4 text-gray-400" />
                            <p className="text-sm font-medium text-gray-700">Description</p>
                          </div>
                          <p className="text-sm text-gray-600 leading-relaxed">
                            {selectedEvent.description}
                          </p>
                        </div>
                      )}
                      
                      {selectedEvent.category && (
                        <div className="mt-4">
                          <span className="badge bg-gray-100 text-gray-700">
                            {selectedEvent.category}
                          </span>
                        </div>
                      )}
                      
                      {/* Meta Info */}
                      <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-400 space-y-1">
                        <p>First seen: {formatDate(selectedEvent.first_seen_at)}</p>
                        <p>Last scraped: {formatDate(selectedEvent.last_scraped_at)}</p>
                        {selectedEvent.is_imported && (
                          <p className="text-purple-600">Imported: {formatDate(selectedEvent.imported_at)}</p>
                        )}
                      </div>
                    </div>
                    
                    {/* Actions */}
                    <div className="p-4 bg-gray-50 rounded-b-2xl">
                      {selectedEvent.is_imported ? (
                        <button
                          onClick={() => handleUnimportEvent(selectedEvent.id)}
                          className="w-full btn-secondary text-red-600 hover:bg-red-50 hover:border-red-200"
                        >
                          <XMarkIcon className="w-5 h-5 mr-2" />
                          Remove Import
                        </button>
                      ) : (
                        <button
                          onClick={() => {
                            setEventToImport(selectedEvent)
                            setShowImportDialog(true)
                          }}
                          className="w-full btn-primary"
                        >
                          <PlusIcon className="w-5 h-5 mr-2" />
                          Import to Platform
                        </button>
                      )}
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-8 text-center"
                  >
                    <InformationCircleIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">Select an event to view details</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>

      {/* Import Dialog */}
      <Transition appear show={showImportDialog} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setShowImportDialog(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all">
                  <div className="p-6">
                    <Dialog.Title className="text-lg font-bold text-gray-900 mb-2">
                      Import Event
                    </Dialog.Title>
                    <Dialog.Description className="text-sm text-gray-500 mb-4">
                      Import "{eventToImport?.title}" to your platform.
                    </Dialog.Description>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Notes (optional)
                      </label>
                      <textarea
                        value={importNotes}
                        onChange={(e) => setImportNotes(e.target.value)}
                        placeholder="Add any notes about this import..."
                        rows={3}
                        className="input"
                      />
                    </div>
                    
                    <div className="flex gap-3">
                      <button
                        onClick={() => setShowImportDialog(false)}
                        className="flex-1 btn-secondary"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleImportEvent}
                        className="flex-1 btn-primary"
                      >
                        <CheckCircleIcon className="w-5 h-5 mr-2" />
                        Import
                      </button>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  )
}
