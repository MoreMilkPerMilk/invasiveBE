# MongoDB Design

## Table of Contents

- [Council](#council)
- [Location](#location)
- [Species](#species)
- [User](#user)
- [Community](#community)
- [Task](#task)

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

- name
- suburbs
- councils
- members
- boundary
- tasks 
- other - reporting etc. ?

## Task <a name="task"></a>

- name
- person
- description
- council 
- community