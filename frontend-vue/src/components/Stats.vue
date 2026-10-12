<script setup>
    import {ref} from 'vue'
    const shotType = ref('2PT Field Goal')
    const shotZone = ref('Mid-Range')
    const actionType = ref('Jump Shot')
</script>

<template>
    <div>
        <label for="shot-type">Shot type</label>

        <select id="shot-type" v-model="shotType">
            <option value="2PT Field Goal">2-point shot</option>
            <option value="3PT Field Goal">3-point shot</option>
        </select>
    </div>

    <div>
        <lable for="shot-zone" v-model="shotZone"> Shot Zone</lable>
        <option value="Restricted Area">Restricted Area</option>
        <option value="In The Paint (Non-RA)">In The Paint (Non-RA)</option>
        <option value="Mid-Range">Mid-Range</option>
        <option value="Left Corner 3">Left Corner 3</option>
        <option value="Right Corner 3">Right Corner 3</option>
        <option value="Above the Break 3">Above the Break 3</option>
        <option value="Backcourt">Backcourt</option>
    </div>

    <div>
        <label for="action-type" v-model="actionType">Action Type</label>
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
    </div>

  
</template>