select 
    *,
    case
		when condition = 'Felújítandó'    	then 1
		when condition = 'Átlagos' 	    	then 2
		when condition = 'Jó állapotú'    	then 3
		when condition = 'Újszerű' 	    	then 4
		when condition = 'Felújított' 		then 4
		when condition = 'Új építésű' 		then 5
		when condition = 'Építés alatt' 	then 5
		when condition = 'Szerkezetkész' 	then 5
		when condition = 'Ismeretlen'     	then 3
	end as condition_score
from {{ ref('stg_zenga__listing_versions') }}