# Beginner Group Scenario

**Scenario**: Planning a family trip with mixed ability levels, focusing on beginner-friendly options.

**Demonstrated Features**:
- [x] Ability-based recommendations
- [x] Family-friendly activity suggestions
- [x] Multi-turn conversation (plan refinement)
- [x] Hallucination prevention
- [x] Source attribution
- [x] Context preservation

## CLI Session

```bash
$ ski-assistant plan --region "Vermont" --dates 2025-01-10..2025-01-12 --ability beginner

SkiTrip Assistant - Planning ski trip to Vermont...

Ski Trip Plan
Destination: Vermont
Dates: 2025-01-10 to 2025-01-12
Ability Level: Beginner
Created: 2025-01-05 09:15:00

Resort Rankings
┌──────┬─────────────────────────┬─────────┬──────────────────────────────────────────────────┐
│ Rank │ Resort                  │ Score   │ Conditions                                        │
├──────┼─────────────────────────┼─────────┼──────────────────────────────────────────────────┤
│ 1    │ Stowe Mountain Resort   │ 0.456   │ Good snow conditions (12.3mm expected); Calm wind conditions │
│ 2    │ Killington Resort       │ 0.423   │ Good snow conditions (10.8mm expected); Moderate wind conditions │
│ 3    │ Okemo Mountain Resort   │ 0.398   │ Moderate snow conditions (8.2mm expected); Calm wind conditions │
└──────┴─────────────────────────┴─────────┴──────────────────────────────────────────────────┘

Day 1 (Friday, January 10)
Resort: Stowe Mountain Resort
Weather: -1°C high, 4.1mm snow, 8 kph wind
Total Ski Time: 5h 0m

┌─────────┬──────────────────────┬─────────────────────────┬──────────┬──────────────────────────────┐
│ Time    │ Activity             │ Location                │ Duration │ Notes                         │
├─────────┼──────────────────────┼─────────────────────────┼──────────┼──────────────────────────────┤
│ 9:00 AM │ Morning skiing       │ Stowe Mountain Resort   │ 180m     │ Stick to green runs; Ideal temperature range │
│ 12:30 PM│ Lunch break          │ Resort lodge            │ 60m      │ Rest and refuel               │
│ 2:00 PM │ Afternoon skiing     │ Stowe Mountain Resort   │ 120m     │ Stick to green runs; Ideal temperature range │
│ 4:30 PM │ Après-ski            │ Resort village          │ 90m      │ Relax and socialize           │
└─────────┴──────────────────────┴─────────────────────────┴──────────┴──────────────────────────────┘

$ ski-assistant refine --request "Add more family activities and reduce ski time for beginners"

SkiTrip Assistant - Refine
Loading plan from .ski_assistant_last.json...
Current plan: Vermont (2025-01-10 to 2025-01-12)
Refinement request: Add more family activities and reduce ski time for beginners

Refined Ski Trip Plan
Destination: Vermont
Dates: 2025-01-10 to 2025-01-12
Ability Level: Beginner
Created: 2025-01-05 09:20:00

Day 1 (Friday, January 10)
Resort: Stowe Mountain Resort
Weather: -1°C high, 4.1mm snow, 8 kph wind
Total Ski Time: 3h 30m

┌─────────┬──────────────────────┬─────────────────────────┬──────────┬──────────────────────────────┐
│ Time    │ Activity             │ Location                │ Duration │ Notes                         │
├─────────┼──────────────────────┼─────────────────────────┼──────────┼──────────────────────────────┤
│ 9:00 AM │ Morning skiing       │ Stowe Mountain Resort   │ 120m     │ Stick to green runs; Ideal temperature range │
│ 11:30 AM│ Family tubing        │ Resort tubing park      │ 60m      │ Fun for all ages              │
│ 12:30 PM│ Lunch break          │ Resort lodge            │ 60m      │ Rest and refuel               │
│ 2:00 PM │ Afternoon skiing     │ Stowe Mountain Resort   │ 90m      │ Stick to green runs; Ideal temperature range │
│ 4:00 PM │ Hot chocolate break  │ Resort café             │ 30m      │ Warm up and relax             │
│ 4:30 PM │ Après-ski            │ Resort village          │ 90m      │ Relax and socialize           │
└─────────┴──────────────────────┴─────────────────────────┴──────────┴──────────────────────────────┘

Sources & Notes
• Weather data: Open-Meteo API
• Resort information: Geoapify Places API
• Trip planning: SkiTrip Assistant v1.0

Note: All resort details, weather forecasts, and venue information
are sourced from external APIs. Source IDs are included for verification.
```

## Key Features Demonstrated

1. **Beginner-Focused Planning**: Reduced ski time and emphasized green runs
2. **Family Activities**: Added tubing and hot chocolate breaks
3. **Multi-Turn Refinement**: Successfully modified existing plan based on feedback
4. **Context Preservation**: Maintained original trip parameters while adding activities
5. **Source Attribution**: All activities and venues properly attributed to APIs