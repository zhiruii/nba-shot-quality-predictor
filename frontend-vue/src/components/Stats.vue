<script setup>
    import {ref} from 'vue'
    const shotType = ref('2PT Field Goal')
    const shotZone = ref('Mid-Range')
    const actionType = ref('Jump Shot')
    const shotDistance = ref(15)
    const locX = ref(0)
    const locY = ref(150)
    const period = ref(2)
    const minutesRemaining = ref(5)
    const secondsRemaining = ref(30)
    const fgPct = ref(0.46)
    const fg3Pct = ref(0.35)
    function predictShot() {
        const shotData = {
            SHOT_DISTANCE: shotDistance.value,
            LOC_X: locX.value,
            LOC_Y: locY.value,
            MINUTES_REMAINING: minutesRemaining.value,
            SECONDS_REMAINING: secondsRemaining.value,
            PERIOD: period.value,
            SHOT_TYPE: shotType.value,
            SHOT_ZONE_BASIC: shotZone.value,
            ACTION_TYPE: actionType.value,
            FG_PCT: fgPct.value,
            FG3_PCT: fg3Pct.value,
        }
    }

</script>

<template>
    <h2>Shot taken</h2>

    <div>
        <label for="loc-x">Court X coordinate (left to right)</label>
        <input
            id="loc-x"
            type="number"
            v-model.number="locX"
            min="-250"
            max="250"
            step="1"
            required
        />
    </div>

    <div>
        <label for="loc-y">Court Y coordinate (baseline to halfcourt)</label>
        <input
            id="loc-y"
            type="number"
            v-model.number="locY"
            min="-47"
            max="422"
            step="1"
            required
        />
    </div>

    <div>
        <label for="shot-distance">Shot distance (feet)</label>
        <input
            id="shot-distance"
            type="number"
            v-model.number="shotDistance"
            min="0"
            max="94"
            step="1"
        />
    </div>

    <div>
        <label for="shot-type">Shot type</label>

        <select id="shot-type" v-model="shotType">
            <option value="2PT Field Goal">2-point shot</option>
            <option value="3PT Field Goal">3-point shot</option>
        </select>
    </div>

    <div>
        <lable for="shot-zone"> Shot Zone</lable>
        <select id="shot-zone" v-model="shotZone">
            <option value="Restricted Area">Restricted Area</option>
            <option value="In The Paint (Non-RA)">In The Paint (Non-RA)</option>
            <option value="Mid-Range">Mid-Range</option>
            <option value="Left Corner 3">Left Corner 3</option>
            <option value="Right Corner 3">Right Corner 3</option>
            <option value="Above the Break 3">Above the Break 3</option>
            <option value="Backcourt">Backcourt</option>
        </select>
    </div>

    <div>
        <label for="action-type">Action Type</label>
        <select id="action-type" v-model="actionType">
            <option value="Jump Shot">Jump Shot</option>
            <option value="Pullup Jump Shot">Pullup Jump Shot</option>
            <option value="Driving Layup">Driving Layup</option>
            <option value="Running Layup">Running Layup</option>
            <option value="Step Back Jump Shot">Step Back Jump Shot</option>
            <option value="Turnaround Jump Shot">Turnaround Jump Shot</option>
            <option value="Cutting Layup Shot">Cutting Layup Shot</option>
            <option value="Fadeaway Jump Shot">Fadeaway Jump Shot</option>
            <option value="Floating Jump Shot">Floating Jump Shot</option>
            <option value="Layup">Layup</option>
            <option value="Dunk">Dunk</option>
            <option value="Hook Shot">Hook Shot</option>
            <option value="Putback Dunk Shot">Putback Dunk Shot</option>
        </select>
    </div>

    <h2>Game situation</h2>

    <div>
        <label for="period">Period</label>
        <input
            id="period"
            type="number"
            v-model.number="period"
            min="1"
            max="7"
            step="1"
            required
        />
    </div>

    <div>
        <label for="minutes-remaining">Minutes remaining</label>
        <input
            id="minutes-remaining"
            type="number"
            v-model.number="minutesRemaining"
            min="0"
            max="11"
            step="1"
            required
        />
    </div>

    <div>
        <label for="seconds-remaining">Seconds remaining</label>
        <input
            id="seconds-remaining"
            type="number"
            v-model.number="secondsRemaining"
            min="0"
            max="59"
            step="1"
            required
        />
    </div>

    <h2>Shooter ability</h2>
    <p>Enter shooting percentages as decimals: 0.46 means 46%.</p>

    <div>
        <label for="fg-pct">Field goal percentage (0–1)</label>
        <input
            id="fg-pct"
            type="number"
            v-model.number="fgPct"
            min="0"
            max="1"
            step="0.01"
            required
        />
    </div>

    <div>
        <label for="fg3-pct">Three-point percentage (0–1)</label>
        <input
            id="fg3-pct"
            type="number"
            v-model.number="fg3Pct"
            min="0"
            max="1"
            step="0.01"
            required
        />
    </div>
    <button type="button" @click="predictShot">
        Predict
    </button>
</template>