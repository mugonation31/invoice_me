-- ============================================================
-- Invoice Me: Base Tables Migration
-- ============================================================

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- ============================================================
-- 1. clients
-- ============================================================
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clients_user_id ON clients(user_id);

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own clients"
    ON clients
    FOR SELECT
    USING ((select auth.uid()) = user_id);

CREATE POLICY "Users can insert their own clients"
    ON clients
    FOR INSERT
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can update their own clients"
    ON clients
    FOR UPDATE
    USING ((select auth.uid()) = user_id)
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can delete their own clients"
    ON clients
    FOR DELETE
    USING ((select auth.uid()) = user_id);

CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 2. company_settings
-- ============================================================
CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name TEXT,
    company_email TEXT,
    company_phone TEXT,
    bank_account_name TEXT,
    bank_name TEXT,
    account_number TEXT,
    sort_code TEXT,
    iban TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_company_settings_user_id ON company_settings(user_id);

ALTER TABLE company_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own company settings"
    ON company_settings
    FOR SELECT
    USING ((select auth.uid()) = user_id);

CREATE POLICY "Users can insert their own company settings"
    ON company_settings
    FOR INSERT
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can update their own company settings"
    ON company_settings
    FOR UPDATE
    USING ((select auth.uid()) = user_id)
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can delete their own company settings"
    ON company_settings
    FOR DELETE
    USING ((select auth.uid()) = user_id);

CREATE TRIGGER update_company_settings_updated_at
    BEFORE UPDATE ON company_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 3. invoices
-- ============================================================
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    invoice_number TEXT NOT NULL,
    status TEXT CHECK (status IN ('draft', 'sent', 'paid', 'overdue')) DEFAULT 'draft',
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    subtotal DECIMAL(12,2) DEFAULT 0.00,
    tax_amount DECIMAL(12,2) DEFAULT 0.00,
    total_due DECIMAL(12,2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, invoice_number)
);

CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_client_id ON invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own invoices"
    ON invoices
    FOR SELECT
    USING ((select auth.uid()) = user_id);

CREATE POLICY "Users can insert their own invoices"
    ON invoices
    FOR INSERT
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can update their own invoices"
    ON invoices
    FOR UPDATE
    USING ((select auth.uid()) = user_id)
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can delete their own invoices"
    ON invoices
    FOR DELETE
    USING ((select auth.uid()) = user_id);

CREATE TRIGGER update_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 4. invoice_line_items
-- ============================================================
CREATE TABLE IF NOT EXISTS invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL DEFAULT 1,
    rate DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoice_line_items_invoice_id ON invoice_line_items(invoice_id);

ALTER TABLE invoice_line_items ENABLE ROW LEVEL SECURITY;

-- Line items use the parent invoice's user_id for RLS
CREATE POLICY "Users can view their own invoice line items"
    ON invoice_line_items
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM invoices
            WHERE invoices.id = invoice_line_items.invoice_id
            AND invoices.user_id = (select auth.uid())
        )
    );

CREATE POLICY "Users can insert their own invoice line items"
    ON invoice_line_items
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM invoices
            WHERE invoices.id = invoice_line_items.invoice_id
            AND invoices.user_id = (select auth.uid())
        )
    );

CREATE POLICY "Users can update their own invoice line items"
    ON invoice_line_items
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM invoices
            WHERE invoices.id = invoice_line_items.invoice_id
            AND invoices.user_id = (select auth.uid())
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM invoices
            WHERE invoices.id = invoice_line_items.invoice_id
            AND invoices.user_id = (select auth.uid())
        )
    );

CREATE POLICY "Users can delete their own invoice line items"
    ON invoice_line_items
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM invoices
            WHERE invoices.id = invoice_line_items.invoice_id
            AND invoices.user_id = (select auth.uid())
        )
    );

-- ============================================================
-- 5. invoice_schedules
-- ============================================================
CREATE TABLE IF NOT EXISTS invoice_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    description TEXT,
    line_items JSONB NOT NULL DEFAULT '[]',
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    recurrence TEXT CHECK (recurrence IN ('once', 'weekly', 'monthly', 'quarterly', 'yearly')),
    next_run_date DATE NOT NULL,
    auto_send BOOLEAN DEFAULT false,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoice_schedules_user_id ON invoice_schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_invoice_schedules_client_id ON invoice_schedules(client_id);
CREATE INDEX IF NOT EXISTS idx_invoice_schedules_next_run_date ON invoice_schedules(next_run_date);

ALTER TABLE invoice_schedules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own invoice schedules"
    ON invoice_schedules
    FOR SELECT
    USING ((select auth.uid()) = user_id);

CREATE POLICY "Users can insert their own invoice schedules"
    ON invoice_schedules
    FOR INSERT
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can update their own invoice schedules"
    ON invoice_schedules
    FOR UPDATE
    USING ((select auth.uid()) = user_id)
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can delete their own invoice schedules"
    ON invoice_schedules
    FOR DELETE
    USING ((select auth.uid()) = user_id);

CREATE TRIGGER update_invoice_schedules_updated_at
    BEFORE UPDATE ON invoice_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
