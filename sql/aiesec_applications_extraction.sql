SELECT "public"."opportunity_applications".an_status      AS an_status,
       "public"."opportunity_applications".opportunity_id AS opportunity_id
FROM   "public"."opportunity_applications"
LIMIT 10000000;
