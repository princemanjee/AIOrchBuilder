-- File: auth/policies.sql
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own contact_messages" 
ON contact_messages FOR SELECT 
USING (auth.uid() = created_by);
