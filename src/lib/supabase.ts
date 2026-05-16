import { createClient, SupabaseClient } from '@supabase/supabase-js'

const hubUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const hubKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

export const hubClient = (hubUrl && hubKey) ? createClient(hubUrl, hubKey) : null as any;

const satellites: Record<string, SupabaseClient> = {}

export const getSatelliteClient = (projectId: string, url?: string, key?: string) => {
  if (satellites[projectId]) return satellites[projectId]
  
  if (url && key) {
    const client = createClient(url, key)
    satellites[projectId] = client
    return client
  }
  
  return null
}
