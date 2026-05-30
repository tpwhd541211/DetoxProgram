import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://ttxkknefkcepctezomvh.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "sb_publishable_AyCa01GmVrxFW2QJUMkPMQ_g2ZL7Lfo";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
