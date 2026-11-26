-- Transaction counts by vehicle type
SELECT vehicle_type, COUNT(*) AS transactions
FROM toll_transactions GROUP BY vehicle_type ORDER BY transactions DESC;

-- Daily toll traffic
SELECT DATE(event_timestamp) AS event_date, COUNT(*) AS transactions
FROM toll_transactions GROUP BY event_date ORDER BY event_date;

-- Busiest toll plazas
SELECT tollplaza_id, COUNT(*) AS transactions
FROM toll_transactions GROUP BY tollplaza_id ORDER BY transactions DESC LIMIT 10;

-- Payment code distribution
SELECT payment_code, COUNT(*) AS transactions
FROM toll_transactions GROUP BY payment_code ORDER BY transactions DESC;
