```
(:PA)
PK -> Core
Company
Variant
TimetableYear
StartDate //není použito

(:TR)
PK -> Core
Company
Variant
TimetableYear
StartDate //není použito

// může být definovaný i v elementu CZPTTHeader
(:Station)
PK -> LocationPrimaryNumber
PrimaryLocationName
CountryCodeISO

(:File)
Name
Procesed

(:Day)
Datetime

(:File) -[:PRECEEDS]-> (:File)

(:File) -[:DEFINES]-> (:PA)

(:File) -[:CANCELS]-> (:PA)

(:PA) -[:RELATED]- (:PA) // Pokud spoj nahrazuje jiný

(:PA) -[:SERVED_BY]- (:TR)

(:PA) -[:GOES_IN]-> (:Day)

(:PA) -[:IS_IN]- (:Station)
LocationSubsidiaryTypeCode //atribut
LocationSubsidiaryCode
AllocationCompany
LocationSubsidiaryName
ALA // příjezd
ALAOffest
ALD // odjezd
ALDOffset
DwellTime
ResponsibleRU
ResponsibleIM
TrainType // musí být 1, jinak se nenabízí cestujícím
TrafficType
CommercialTrafficType
TrainAvtivityType // musí být 0001, jinak vlak v zastávce nestojí, pole
AssociatedAttachedTrainID //nepoužívá se
AssociatedAttachedOTN // nenašel jsem, že se používá
OperationalTrainNumber
NetworkSpecificParameters // ve formátu name:value
```