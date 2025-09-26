-- 1. Basic SELECT with LIMIT (Simple data inspection)
SELECT * FROM airline LIMIT 10;

-- 2. Filtering with WHERE and sorting with ORDER BY
SELECT airline_name, airline_country, created_at 
FROM airline 
WHERE created_at > '2024-01-01'
ORDER BY created_at DESC;

-- 3. Aggregation with GROUP BY and COUNT
SELECT airline_country, COUNT(*) as airline_count
FROM airline 
GROUP BY airline_country 
ORDER BY airline_count DESC;

-- 4. Aggregation with AVG, MIN, MAX
SELECT 
    AVG(weight_in_kg) as average_weight,
    MIN(weight_in_kg) as min_weight,
    MAX(weight_in_kg) as max_weight
FROM baggage;

-- 5. JOIN between two tables (Corrected join condition)
SELECT a.airline_name, b.weight_in_kg
FROM airline a
JOIN baggage b ON a.airline_id = b.baggage_id
LIMIT 10;

-- 6. Baggage check results analysis
SELECT check_result, COUNT(*) as result_count
FROM baggage_check 
GROUP BY check_result 
ORDER BY result_count DESC;

-- 7. Heavy baggage analysis (>30kg)
SELECT COUNT(*) as heavy_baggage_count
FROM baggage 
WHERE weight_in_kg > 30;

-- 8. Monthly baggage creation pattern
SELECT 
    EXTRACT(MONTH FROM created_date) as month_number,
    COUNT(*) as baggage_count
FROM baggage 
GROUP BY month_number 
ORDER BY month_number;

-- 9. Airlines with missing codes
SELECT airline_name, airline_country 
FROM airline 
WHERE airline_code IS NULL;

-- 10. Complex JOIN with multiple tables
SELECT 
    a.airline_name,
    b.weight_in_kg,
    bc.check_result,
    bp.seat
FROM airline a
JOIN baggage b ON a.airline_id = b.baggage_id
JOIN baggage_check bc ON b.booking_id = bc.booking_id
JOIN boarding_pass bp ON b.booking_id = bp.booking_id
LIMIT 10;