import { Event } from '../types'
import { format, parseISO } from 'date-fns'
import { CalendarIcon, MapPinIcon, TagIcon } from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'
import clsx from 'clsx'

interface EventCardProps {
  event: Event
  onGetTickets: (event: Event) => void
}

export default function EventCard({ event, onGetTickets }: EventCardProps) {
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return event.date_string || 'Date TBA'
    try {
      return format(parseISO(dateStr), 'EEE, MMM d, yyyy • h:mm a')
    } catch {
      return event.date_string || dateStr
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { class: string; label: string }> = {
      new: { class: 'badge-new', label: '✨ New' },
      updated: { class: 'badge-updated', label: '🔄 Updated' },
      inactive: { class: 'badge-inactive', label: 'Inactive' },
      imported: { class: 'badge-imported', label: '✓ Imported' },
    }
    return badges[status] || badges.new
  }

  const badge = getStatusBadge(event.status)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="card group overflow-hidden"
    >
      {/* Image Section */}
      <div className="relative h-48 overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200">
        {event.image_url ? (
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none'
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <CalendarIcon className="w-16 h-16 text-gray-300" />
          </div>
        )}
        
        {/* Status Badge */}
        <div className="absolute top-3 right-3">
          <span className={clsx('badge', badge.class)}>
            {badge.label}
          </span>
        </div>
        
        {/* Source Badge */}
        <div className="absolute top-3 left-3">
          <span className="badge bg-black/50 text-white backdrop-blur-sm">
            {event.source_name}
          </span>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-5">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 mb-3 group-hover:text-primary-600 transition-colors">
          {event.title}
        </h3>

        <div className="space-y-2 mb-4">
          <div className="flex items-start gap-2 text-sm text-gray-600">
            <CalendarIcon className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
            <span className="line-clamp-1">{formatDate(event.date_time)}</span>
          </div>
          
          {event.venue_name && (
            <div className="flex items-start gap-2 text-sm text-gray-600">
              <MapPinIcon className="w-5 h-5 text-sydney-500 flex-shrink-0 mt-0.5" />
              <span className="line-clamp-1">{event.venue_name}</span>
            </div>
          )}
          
          {event.category && (
            <div className="flex items-start gap-2 text-sm text-gray-600">
              <TagIcon className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
              <span className="line-clamp-1">{event.category}</span>
            </div>
          )}
        </div>

        {event.description && (
          <p className="text-sm text-gray-500 line-clamp-2 mb-4">
            {event.description}
          </p>
        )}

        <button
          onClick={() => onGetTickets(event)}
          className="w-full btn-primary text-sm"
        >
          Get Tickets
        </button>
      </div>
    </motion.div>
  )
}
