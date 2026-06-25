(define (domain smart_campus)
  (:requirements :strips :typing :fluents :durative-actions :timed-initial-literals)

  (:types room air_conditioner light)

  (:predicates
    (operating_hour)
    (work_time)
    (out_work_time)
    (peak_hours)
    (ac_on ?r - room ?a - air_conditioner)
    (ac_off ?r - room ?a - air_conditioner)
    (light_on ?r - room ?l - light)
    (light_off ?r - room ?l - light)
  )

  (:functions
    (people_in_room ?r - room)
    (ac_temperature ?a - air_conditioner)
    (metric_total_cost)
  )

  (:durative-action start_campus_operating
    :parameters ()
    :duration (= ?duration 15.0)
    :condition (and 
      (at start (operating_hour))
      (over all (operating_hour))
    )
    :effect (and 
      (at start (work_time))
      (at end (out_work_time))
    )
  )

  (:durative-action turn_on_air_conditioner
    :parameters (?r - room ?a - air_conditioner)
    :duration (= ?duration 2.0)
    :condition (and 
      (at start (work_time))
      (over all (> (people_in_room ?r) 0))
    )
    :effect (and 
      (at start (ac_on ?r ?a))
      (at end (increase (metric_total_cost) 4))
    )
  )

    (:durative-action turn_on_air_conditioner_peak_hours
    :parameters (?r - room ?a - air_conditioner)
    :duration (= ?duration 3.0)
    :condition (and 
      (at start (work_time))
      (at start (peak_hours))
      (over all (> (people_in_room ?r) 0))
    )
    :effect (and 
      (at start (ac_on ?r ?a))
      (at end (increase (metric_total_cost) 2))
    )
  )

  (:durative-action turn_off_air_conditioner
    :parameters (?r - room ?a - air_conditioner)
    :duration (= ?duration 1.0)
    :condition (and 
      (at start (ac_on ?r ?a))
      (over all (= (people_in_room ?r) 0))
    )
    :effect (and 
      (at start (ac_off ?r ?a))
    )
  )

  (:durative-action turn_on_light
    :parameters (?r - room ?l - light)
    :duration (= ?duration 2.0)
    :condition (and 
      (at start (work_time))
      (over all (> (people_in_room ?r) 0))
    )
    :effect (and 
      (at start (light_on ?r ?l))
      (at end (increase (metric_total_cost) 2))
    )
  )

  (:durative-action turn_off_light
    :parameters (?r - room ?l - light)
    :duration (= ?duration 1.0)
    :condition (and 
      (at start (light_on ?r ?l))
      (over all (= (people_in_room ?r) 0))
    )
    :effect (and 
      (at start (light_off ?r ?l))
    )
  )

  (:durative-action set_ac_temperature_25
      :parameters (?r - room ?a - air_conditioner)
      :duration (= ?duration 3.0)
      :condition (and 
        (at start (ac_on ?r ?a))
        (at start (peak_hours))
        (over all (peak_hours))
      )
      :effect (and 
        (at start (assign (ac_temperature ?a) 25))
        (at end (decrease (metric_total_cost) 1))
      )
  ) 
)