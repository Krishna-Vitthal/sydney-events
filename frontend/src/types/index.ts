export interface User {
  id: number
  email: string
  name: string | null
  picture: string | null
  is_active: boolean
  is_admin: boolean
  created_at: string
}

export interface Event {
  id: number
  title: string
  date_time: string | null
  date_string: string | null
  venue_name: string | null
  venue_address: string | null
  city: string
  description: string | null
  category: string | null
  tags: string | null
  image_url: string | null
  source_name: string
  source_url: string
  status: 'new' | 'updated' | 'inactive' | 'imported'
  last_scraped_at: string
  first_seen_at: string
  is_imported: boolean
  imported_at: string | null
  imported_by_id: number | null
  import_notes: string | null
}

export interface EventListResponse {
  events: Event[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface DashboardStats {
  total_events: number
  new_events: number
  updated_events: number
  inactive_events: number
  imported_events: number
  total_leads: number
  sources: string[]
}

export interface TicketLead {
  email: string
  consent: boolean
  event_id: number
}

export interface EventFilter {
  city?: string
  keyword?: string
  date_from?: string
  date_to?: string
  status?: string
  source?: string
  page?: number
  per_page?: number
}
