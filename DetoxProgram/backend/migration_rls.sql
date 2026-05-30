-- 1. Enable Row Level Security (RLS) on all user-owned tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_file ENABLE ROW LEVEL SECURITY;
ALTER TABLE score_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_job ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE norm_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE nlp_result ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_session ENABLE ROW LEVEL SECURITY;
ALTER TABLE mission_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_streak ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing policies if any to avoid duplication errors
DROP POLICY IF EXISTS user_profiles_policy ON profiles;
DROP POLICY IF EXISTS user_consent_log_policy ON consent_log;
DROP POLICY IF EXISTS user_raw_file_policy ON raw_file;
DROP POLICY IF EXISTS user_score_run_policy ON score_run;
DROP POLICY IF EXISTS user_report_snapshot_policy ON report_snapshot;
DROP POLICY IF EXISTS user_analysis_job_policy ON analysis_job;
DROP POLICY IF EXISTS user_raw_event_policy ON raw_event;
DROP POLICY IF EXISTS user_norm_event_policy ON norm_event;
DROP POLICY IF EXISTS user_nlp_result_policy ON nlp_result;
DROP POLICY IF EXISTS user_user_session_policy ON user_session;
DROP POLICY IF EXISTS user_mission_log_policy ON mission_log;
DROP POLICY IF EXISTS user_user_streak_policy ON user_streak;
DROP POLICY IF EXISTS user_audit_log_policy ON audit_log;

-- 3. Create RLS Policies based on auth.uid() (casted to text for compatibility)
CREATE POLICY user_profiles_policy ON profiles
    FOR ALL USING (id = auth.uid()::text) WITH CHECK (id = auth.uid()::text);

CREATE POLICY user_consent_log_policy ON consent_log
    FOR ALL USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY user_raw_file_policy ON raw_file
    FOR ALL USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY user_score_run_policy ON score_run
    FOR ALL USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY user_report_snapshot_policy ON report_snapshot
    FOR ALL USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY user_analysis_job_policy ON analysis_job
    FOR ALL USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY user_user_session_policy ON user_session
    FOR ALL USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY user_mission_log_policy ON mission_log
    FOR ALL USING (plan_id = auth.uid()::text) WITH CHECK (plan_id = auth.uid()::text);

CREATE POLICY user_user_streak_policy ON user_streak
    FOR ALL USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY user_audit_log_policy ON audit_log
    FOR ALL USING (false);

-- Relational tables matching via dataset_id or analysis_id back to analysis_job ownership
CREATE POLICY user_raw_event_policy ON raw_event
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM analysis_job
            WHERE analysis_job.dataset_id = raw_event.dataset_id
              AND analysis_job.user_id = auth.uid()::text
        )
    );

CREATE POLICY user_norm_event_policy ON norm_event
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM analysis_job
            WHERE analysis_job.dataset_id = norm_event.dataset_id
              AND analysis_job.user_id = auth.uid()::text
        )
    );

CREATE POLICY user_nlp_result_policy ON nlp_result
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM analysis_job
            WHERE analysis_job.dataset_id = nlp_result.dataset_id
              AND analysis_job.user_id = auth.uid()::text
        )
    );

-- 4. Create the User Self-Deletion PostgreSQL function (Security Definer)
CREATE OR REPLACE FUNCTION delete_user_account()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    DELETE FROM auth.users WHERE id = auth.uid();
END;
$$;
