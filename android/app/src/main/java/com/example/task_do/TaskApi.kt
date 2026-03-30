package com.example.task_do

import retrofit2.http.*

interface TaskApi {
    @GET("api/tasks")
    suspend fun getTasks(): List<String>

    @POST("api/tasks")
    suspend fun updateTasks(@Body tasks: List<String>): retrofit2.Response<Void>

    @GET("api/counters")
    suspend fun getCounters(): CountersResponse
}

data class CountersResponse(val day: String, val total: String)




