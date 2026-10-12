<script setup>
    import {ref} from 'vue'
    const shotType = ref('2PT Field Goal')
    const shotZone = ref('Mid-Range')
    const actionType = ref('Jump Shot')
</script>

<template>
    <label for="shot-type">Shot type</label>

    <select id="shot-type" v-model="shotType">
        <option value="2PT Field Goal">2-point shot</option>
        <option value="3PT Field Goal">3-point shot</option>
    </select>

    <lable for="shot-zone" v-model="shotZone"> Shot Zone</lable>

    <label for="action-type" v-model="actionType">Action Type</label>

  
</template>