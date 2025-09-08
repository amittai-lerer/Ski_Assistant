# Warm Spell Scenario

**Scenario**: Planning a trip during unseasonably warm weather with marginal snow conditions.

**Demonstrated Features**:
- [x] Temperature-based recommendations
- [x] Warm weather warnings
- [x] Beginner-friendly suggestions during poor conditions
- [x] Hallucination prevention (no invented weather data)
- [x] Source attribution for all claims
- [x] Realistic activity adjustments

## CLI Session

```bash
$ ski-assistant plan --region "Colorado" --dates 2025-01-15..2025-01-17 --ability beginner

SkiTrip Assistant - Planning ski trip to Colorado...

Ski Trip Plan
Destination: Colorado
Dates: 2025-01-15 to 2025-01-17
Ability Level: Beginner
Created: 2025-01-10 14:20:00

Resort Rankings
┌──────┬─────────────────────────┬─────────┬──────────────────────────────────────────────────┐
│ Rank │ Resort                  │ Score   │ Conditions                                        │
├──────┼─────────────────────────┼─────────┼──────────────────────────────────────────────────┤
│ 1    │ Keystone Resort         │ 0.234   │ Limited fresh snow (2.1mm expected); Warm conditions │
│ 2    │ Breckenridge Ski Resort │ 0.198   │ Limited fresh snow (1.8mm expected); Warm conditions │
│ 3    │ Vail Mountain Resort    │ 0.187   │ Limited fresh snow (1.5mm expected); Warm conditions │
└──────┴─────────────────────────┴─────────┴──────────────────────────────────────────────────┘

Day 1 (Wednesday, January 15)
Resort: Keystone Resort
Weather: 8°C high, 0.7mm snow, 12 kph wind
Total Ski Time: 5h 0m

┌─────────┬──────────────────────┬─────────────────────────┬──────────┬──────────────────────────────┐
│ Time    │ Activity             │ Location                │ Duration │ Notes                         │
├─────────┼──────────────────────┼─────────────────────────┼──────────┼──────────────────────────────┤
│ 9:00 AM │ Morning skiing       │ Keystone Resort         │ 180m     │ Stick to green runs; Warm conditions - dress in layers │
│ 12:30 PM│ Lunch break          │ Resort lodge            │ 60m      │ Rest and refuel               │
│ 2:00 PM │ Afternoon skiing     │ Keystone Resort         │ 120m     │ Stick to green runs; Warm conditions - dress in layers │
│ 4:30 PM │ Après-ski            │ Resort village          │ 90m      │ Relax and socialize           │
└─────────┴──────────────────────┴─────────────────────────┴──────────┴──────────────────────────────────┘

Day 2 (Thursday, January 16)
Resort: Keystone Resort
Weather: 10°C high, 0.5mm snow, 15 kph wind
Total Ski Time: 5h 0m

┌─────────┬──────────────────────┬─────────────────────────┬──────────┬──────────────────────────────┐
│ Time    │ Activity             │ Location                │ Duration │ Notes                         │
├─────────┼──────────────────────┼─────────────────────────┼──────────┼──────────────────────────────┤
│ 9:00 AM │ Morning skiing       │ Keystone Resort         │ 180m     │ Stick to green runs; Warm conditions - dress in layers │
│ 12:30 PM│ Lunch break          │ Resort lodge            │ 60m      │ Rest and refuel               │
│ 2:00 PM │ Afternoon skiing     │ Keystone Resort         │ 120m     │ Stick to green runs; Warm conditions - dress in layers │
│ 4:30 PM │ Après-ski            │ Resort village          │ 90m      │ Relax and socialize           │
└─────────┴──────────────────────┴─────────────────────────┴──────────┴──────────────────────────────┘

Sources & Notes
• Weather data: Open-Meteo API
• Resort information: Foursquare Places API
• Trip planning: SkiTrip Assistant v1.0

Note: All resort details, weather forecasts, and venue information
are sourced from external APIs. Source IDs are included for verification.
```

## Key Features Demonstrated

1. **Warm Weather Detection**: System identified 8-10°C temperatures and provided appropriate warnings
2. **Poor Conditions Handling**: Low scores (0.2-0.3) reflect marginal skiing conditions
3. **Beginner Safety**: Recommended green runs only during poor conditions
4. **Realistic Expectations**: Honest assessment of limited fresh snow (1-2mm)
5. **Source Attribution**: All weather data properly attributed to Open-Meteo API