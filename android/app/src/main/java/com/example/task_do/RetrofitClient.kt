package com.example.task_do

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    private var currentBaseUrl = "http://192.168.1.40:17789/"
    private var retrofit: Retrofit? = null
    private var api: TaskApi? = null

    fun getInstance(): TaskApi {
        if (api == null || retrofit?.baseUrl().toString() != currentBaseUrl) {
            retrofit = Retrofit.Builder()
                .baseUrl(currentBaseUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            api = retrofit?.create(TaskApi::class.java)
        }
        return api!!
    }

    fun setBaseUrl(newUrl: String) {
        currentBaseUrl = newUrl
        retrofit = null
        api = null
    }
}