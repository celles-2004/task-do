package com.example.task_do

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    // Замените IP на адрес вашего компьютера в локальной сети
    private const val BASE_URL = "http://192.168.1.40:17789/"

    val instance: TaskApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(TaskApi::class.java)
    }
}