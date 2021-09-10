# MongoDB Design

## Table of Contents

- [Council](#council)
- [Location](#location)
- [Species](#species)
- [User](#user)
- [Community](#community)
- [Report] (#report)

## Council <a name = "council"></a>

- id
- name
- species_occuring
- boundary 
- lga_code
- abbreviated_name
- area_sqkm
- suburbs (TODO!)

## Location <a name = "location"></a>

- id 
- name 
- point 
- weeds_present
- others?

## Species <a name = "species"></a>

- species_id
- name
- growth_form
- info
- family 
- native 
- flower_colour 
- flowering_time 
- leaf_arrangement 
- common_names 
- notifiable 
- control_methods 
- replacement_species 
- state declaration 

## User <a name = "user"></a>

- person_id
- first_name 
- last_name 
- date_joined 
- count_identified 
- previous_tags 
- location

## Community FEATURES NOT MODEL (TODO!) <a name="community"></a>

- community name
- suburb / council?
- other - reporting etc.
- encapsulate the addition of multiple areas to a single community
- maybe encapsulate that Councils are actually Communities, 
and have communities as the main target which has a variable 
which names whether something is a Council etc? 

## Report <a name="report"></a>
- idea: collate user data into a report for council to make reporting process more efficient and eliminiate redundant data
- area name - if available some colloquial name e.g. "Sutton's Creek" 
- Locations 
- images?
- report status (stage with Council etc.) {pending council, feedback, investigating, DONE} 
 