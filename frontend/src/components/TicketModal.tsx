import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon, EnvelopeIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { Event } from '../types'
import { eventsApi } from '../api'
import { format, parseISO } from 'date-fns'
import toast from 'react-hot-toast'

interface TicketModalProps {
  event: Event | null
  isOpen: boolean
  onClose: () => void
}

export default function TicketModal({ event, isOpen, onClose }: TicketModalProps) {
  const [email, setEmail] = useState('')
  const [consent, setConsent] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!event) return

    setIsSubmitting(true)
    try {
      await eventsApi.createTicketLead({
        email,
        consent,
        event_id: event.id,
      })
      setIsSuccess(true)
      toast.success('Thank you! Redirecting to tickets...')
      
      // Redirect after short delay
      setTimeout(() => {
        window.open(event.source_url, '_blank')
        handleClose()
      }, 1500)
    } catch (error) {
      toast.error('Something went wrong. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    setEmail('')
    setConsent(false)
    setIsSuccess(false)
    onClose()
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return event?.date_string || 'Date TBA'
    try {
      return format(parseISO(dateStr), 'EEEE, MMMM d, yyyy • h:mm a')
    } catch {
      return event?.date_string || dateStr
    }
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
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
                {/* Header */}
                <div className="relative">
                  {event?.image_url ? (
                    <div className="h-40 overflow-hidden">
                      <img
                        src={event.image_url}
                        alt={event.title}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                    </div>
                  ) : (
                    <div className="h-24 bg-gradient-to-r from-primary-500 to-sydney-500" />
                  )}
                  
                  <button
                    onClick={handleClose}
                    className="absolute top-3 right-3 p-2 rounded-full bg-white/90 hover:bg-white transition-colors"
                  >
                    <XMarkIcon className="w-5 h-5 text-gray-600" />
                  </button>
                </div>

                {/* Content */}
                <div className="p-6">
                  <Dialog.Title className="text-xl font-bold text-gray-900 mb-2">
                    {event?.title}
                  </Dialog.Title>
                  
                  <p className="text-sm text-gray-500 mb-6">
                    {formatDate(event?.date_time || null)}
                  </p>

                  {isSuccess ? (
                    <div className="text-center py-8">
                      <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        You're all set!
                      </h3>
                      <p className="text-gray-500">
                        Redirecting you to get your tickets...
                      </p>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmit} className="space-y-4">
                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                          Your email address
                        </label>
                        <div className="relative">
                          <EnvelopeIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                          <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@example.com"
                            required
                            className="input pl-10"
                          />
                        </div>
                      </div>

                      <label className="flex items-start gap-3 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={consent}
                          onChange={(e) => setConsent(e.target.checked)}
                          className="mt-1 w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm text-gray-600 group-hover:text-gray-900 transition-colors">
                          I agree to receive event updates and promotional emails. 
                          You can unsubscribe at any time.
                        </span>
                      </label>

                      <button
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isSubmitting ? (
                          <span className="flex items-center justify-center gap-2">
                            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                              <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                                fill="none"
                              />
                              <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                              />
                            </svg>
                            Processing...
                          </span>
                        ) : (
                          'Continue to Tickets'
                        )}
                      </button>

                      <p className="text-xs text-center text-gray-400">
                        You'll be redirected to {event?.source_name} to complete your purchase.
                      </p>
                    </form>
                  )}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
