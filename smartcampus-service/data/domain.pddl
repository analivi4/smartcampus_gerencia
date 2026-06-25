(define (domain smart_campus)
  (:requirements :strips :typing :fluents :durative-actions :timed-initial-literals :duration-inequalities :continuous-effects)

  (:types room air_conditioner light slot)

  (:predicates
    (operating_hour)
    (work_time)
    (out_work_time)
    (peak_hours)
    (ac_on ?r - room ?a - air_conditioner)
    (ac_off ?r - room ?a - air_conditioner)
    (ac_idle ?r - room ?a - air_conditioner)
    (light_on ?r - room ?l - light)
    (light_off ?r - room ?l - light)
    (light_idle ?r - room ?l - light)
    (class_window_open ?r - room ?s - slot)
    (class_acknowledged ?r - room ?s - slot)
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
    :duration (= ?duration 1.0)
    :condition (and
      (at start (work_time))
      (at start (ac_idle ?r ?a))
      (over all (> (people_in_room ?r) 0))
    )
    :effect (and
      (at start (ac_on ?r ?a))
      (at start (not (ac_idle ?r ?a)))
      (at end (increase (metric_total_cost) 4))
    )
  )

  (:durative-action turn_on_air_conditioner_peak_hours
    :parameters (?r - room ?a - air_conditioner)
    :duration (= ?duration 1.5)
    :condition (and
      (at start (work_time))
      (at start (peak_hours))
      (at start (ac_idle ?r ?a))
      (over all (> (people_in_room ?r) 0))
    )
    :effect (and
      (at start (ac_on ?r ?a))
      (at start (not (ac_idle ?r ?a)))
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
      (at start (not (ac_on ?r ?a)))
      (at start (ac_off ?r ?a))
      (at start (ac_idle ?r ?a))
    )
  )

  (:durative-action turn_on_light
    :parameters (?r - room ?l - light)
    :duration (= ?duration 1.0)
    :condition (and
      (at start (work_time))
      (at start (light_idle ?r ?l))
      (over all (> (people_in_room ?r) 0))
    )
    :effect (and
      (at start (light_on ?r ?l))
      (at start (not (light_idle ?r ?l)))
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
      (at start (not (light_on ?r ?l)))
      (at start (light_off ?r ?l))
      (at start (light_idle ?r ?l))
    )
  )

  (:durative-action ac_idle_penalty
    :parameters (?r - room ?a - air_conditioner)
    :duration (>= ?duration 0.1)
    :condition (and
      (over all (ac_on ?r ?a))
      (over all (= (people_in_room ?r) 0))
      (over all (work_time))
    )
    :effect (increase (metric_total_cost) (* #t 5))
  )

  (:durative-action light_idle_penalty
    :parameters (?r - room ?l - light)
    :duration (>= ?duration 0.1)
    :condition (and
      (over all (light_on ?r ?l))
      (over all (= (people_in_room ?r) 0))
      (over all (work_time))
    )
    :effect (increase (metric_total_cost) (* #t 3))
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

  (:durative-action acknowledge_class
    :parameters (?r - room ?a - air_conditioner ?l - light ?s - slot)
    :duration (= ?duration 0.01)
    :condition (and
      (at start (class_window_open ?r ?s))
      (at start (ac_on ?r ?a))
      (at start (light_on ?r ?l))
    )
    :effect (at end (class_acknowledged ?r ?s))
  )
)
