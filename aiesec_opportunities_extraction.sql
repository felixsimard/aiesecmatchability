SELECT    "public"."opportunities".id AS opportunity_id,
          "public"."opportunities".created_at,
          "public"."opportunities".applications_close_date,
          "public"."opportunities".openings,
          "public"."opportunities".logistics_info,
          "public"."opportunities".transparent_fee_details,
          "public"."opportunities".earliest_start_date,
          "public"."opportunities".latest_end_date,
          "public"."opportunities".duration_min,
          "public"."opportunities".role_info,
          "public"."opportunities".title,
          "public"."opportunities".description,
          "public"."opportunities".legal_info,
          "public"."opportunities".specifics_info,
          "public"."opportunities".google_place_id,
          "public"."opportunities".lat,
          "public"."opportunities".lng,
          "public"."opportunities".profile_photo_file_size,
          "public"."opportunities".cover_photo_file_size,
          "public"."opportunities".project_fee_cents,
          "T3_".NAME                         AS name_region,
          "T2_".NAME                         AS name_entity,
          sub_jd_req.opportunity_background  AS opp_background_req,
          sub_jd_req.opportunity_language    AS opp_language_req,
          sub_jd_req.opportunity_skill       AS opp_skill_req,
          sub_jd_pref.opportunity_background AS opp_background_pref,
          sub_jd_pref.opportunity_language   AS opp_language_pref,
          sub_jd_pref.opportunity_skill      AS opp_skill_pref,
          "public"."opportunities".status, -- I do not know what does it means
          sub_app."matched_or_rejected_at",
          sub_app."experience_start_date",
          sub_app."experience_end_date",
          "P1_".consumer_name AS programme_id
FROM      "public"."opportunities"
          -- Add programme name
LEFT JOIN "public"."programmes" "P1_"
ON        "public"."opportunities"."programme_id" = "P1_"."id"
          -- Add entity and region
LEFT JOIN "public"."offices" "T1_"
ON        "public"."opportunities"."host_lc_id" = "T1_"."id"
LEFT JOIN "public"."offices" "T2_"
ON        "T1_"."parent_id" = "T2_"."id"
LEFT JOIN "public"."offices" "T3_"
ON        "T2_"."parent_id" = "T3_"."id"
          -- When an application is accepted, add its details and some variables on the EP
LEFT JOIN
          (
                     SELECT     "public"."opportunity_applications".opportunity_id,
                                "public"."opportunity_applications"."experience_start_date",
                                "public"."opportunity_applications"."experience_end_date",
                                "public"."opportunity_applications"."matched_or_rejected_at",
                                "public"."opportunity_applications"."status",
                                "public"."people".gender,
                                "public"."people".dob
                     FROM       "public"."opportunity_applications"
                     INNER JOIN "public"."people"
                     ON         "public"."opportunity_applications"."person_id" = "public"."people"."id"
                     WHERE      (
                                           "public"."opportunity_applications"."an_status" = 'accepted') ) AS sub_app
ON        "public"."opportunities".id = sub_app."opportunity_id"
          -- Add required language, background and skills
LEFT JOIN
          (
                   SELECT   sub2.repr_id,
                            String_agg(sub2.names_, ',') filter (WHERE sub2.hierarchie = 'Opportunity-background') AS opportunity_background ,
                            string_agg(sub2.names_, ',') filter (WHERE sub2.hierarchie = 'Opportunity-language')   AS opportunity_language ,
                            string_agg(sub2.names_, ',') filter (WHERE sub2.hierarchie = 'Opportunity-skill')      AS opportunity_skill
                   FROM     (
                                     SELECT   sub.representable_id                                        AS repr_id,
                                                       concat(sub.representable_type, '-', sub.type_name) AS hierarchie,
                                              string_agg(sub.name_, ',')                                  AS names_
                                     FROM    (
                                                         SELECT     representable_id,
                                                                    representable_type,
                                                                    type_name,
                                                                    NAME AS name_
                                                         FROM       "public"."constant_maps"
                                                         INNER JOIN "public"."constants"
                                                         ON         "public"."constant_maps"."constant_id" = "public"."constants"."id"
                                                         WHERE      (
                                                                               "public"."constant_maps"."option" IN ('required') )
                                                         ORDER BY   representable_id,
                                                                    representable_type,
                                                                    type_name,
                                                                    NAME ) AS sub
                                     GROUP BY sub.representable_id,
                                              sub.representable_type,
                                              sub.type_name ) AS sub2
                   GROUP BY sub2.repr_id
                   ORDER BY sub2.repr_id ) AS sub_jd_req
ON        "public"."opportunities".id = sub_jd_req.repr_id
          -- Add preferred language, background and skills
LEFT JOIN
          (
                   SELECT   sub2.repr_id,
                            string_agg(sub2.names_, ',') filter (WHERE sub2.hierarchie = 'Opportunity-background') AS opportunity_background ,
                            string_agg(sub2.names_, ',') filter (WHERE sub2.hierarchie = 'Opportunity-language')   AS opportunity_language ,
                            string_agg(sub2.names_, ',') filter (WHERE sub2.hierarchie = 'Opportunity-skill')      AS opportunity_skill
                   FROM     (
                                     SELECT   sub.representable_id                                        AS repr_id,
                                                       concat(sub.representable_type, '-', sub.type_name) AS hierarchie,
                                              string_agg(sub.name_, ',')                                  AS names_
                                     FROM    (
                                                         SELECT     representable_id,
                                                                    representable_type,
                                                                    type_name,
                                                                    NAME AS name_
                                                         FROM       "public"."constant_maps"
                                                         INNER JOIN "public"."constants"
                                                         ON         "public"."constant_maps"."constant_id" = "public"."constants"."id"
                                                         WHERE      (
                                                                               "public"."constant_maps"."option" IN ('preferred') )
                                                         ORDER BY   representable_id,
                                                                    representable_type,
                                                                    type_name,
                                                                    NAME ) AS sub
                                     GROUP BY sub.representable_id,
                                              sub.representable_type,
                                              sub.type_name ) AS sub2
                   GROUP BY sub2.repr_id
                   ORDER BY sub2.repr_id ) AS sub_jd_pref
ON        "public"."opportunities".id = sub_jd_pref.repr_id limit 100000;
