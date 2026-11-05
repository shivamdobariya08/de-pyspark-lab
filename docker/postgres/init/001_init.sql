CREATE TABLE IF NOT EXISTS public.materialbewegungen (
    bewegung_id BIGINT PRIMARY KEY,
    werk VARCHAR(4) NOT NULL,
    materialnummer VARCHAR(40) NOT NULL,
    menge INTEGER NOT NULL CHECK (menge >= 0),
    buchungsdatum DATE NOT NULL
);

INSERT INTO public.materialbewegungen (
    bewegung_id, werk, materialnummer, menge, buchungsdatum
)
VALUES
    (1, '1000', 'MAT001', 10, '2026-11-01'),
    (2, '1000', 'MAT002', 20, '2026-11-01'),
    (3, '2000', 'MAT003', 10, '2026-11-02'),
    (4, '2000', 'MAT004',  5, '2026-11-02')
ON CONFLICT (bewegung_id) DO NOTHING;
