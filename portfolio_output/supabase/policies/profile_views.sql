-- File: auth/policies.sql
ALTER TABLE profile_views ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile_views" 
ON profile_views FOR SELECT 
USING (auth.uid() = created_by);
