package com.example.task_do

import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var tvDayCounter: TextView
    private lateinit var tvTotalCounter: TextView
    private lateinit var btnRefresh: Button
    private lateinit var fabAdd: FloatingActionButton
    private val tasks = mutableListOf<String>()
    private lateinit var adapter: TaskAdapter
    private lateinit var etServerIp: EditText
    private lateinit var btnSaveIp: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        tvDayCounter = findViewById(R.id.tvDayCounter)
        tvTotalCounter = findViewById(R.id.tvTotalCounter)
        btnRefresh = findViewById(R.id.btnRefresh)
        fabAdd = findViewById(R.id.fabAdd)
        etServerIp = findViewById(R.id.etServerIp)
        btnSaveIp = findViewById(R.id.btnSaveIp)

        adapter = TaskAdapter(tasks) { position ->
            deleteTask(position)
        }
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter

        // Загружаем сохранённый IP
        val savedIp = getSharedPreferences("app_perfs", MODE_PRIVATE).getString("server_IP", "")
        if (!savedIp.isNullOrEmpty()) {
            etServerIp.setText(savedIp)
            RetrofitClient.setBaseUrl("http://$savedIp:17789/")
        } else {
            // Если нет сохранённого, можно оставить дефолтный или попросить ввести
            RetrofitClient.setBaseUrl("http://192.168.1.40:17789/")
        }

        btnSaveIp.setOnClickListener {
            val ip = etServerIp.text.toString().trim()
            if (ip.isNotEmpty()) {
                getSharedPreferences("app_perfs", MODE_PRIVATE).edit().putString("server_ip", ip).apply()
                RetrofitClient.setBaseUrl("http://$ip:17789/")
                Toast.makeText(this, "IP сохранён, перезагрузите список", Toast.LENGTH_SHORT).show()
                loadData()
            } else {
                Toast.makeText(this, "Введите IP", Toast.LENGTH_SHORT).show()
            }
        }

        fabAdd.setOnClickListener { showAddTaskDialog() }
        btnRefresh.setOnClickListener { loadData() }

        loadData()
    }

    private fun loadData() = lifecycleScope.launch(Dispatchers.IO) {
        try {
            val taskList = RetrofitClient.getInstance().getTasks()
            withContext(Dispatchers.Main) {
                tasks.clear()
                tasks.addAll(taskList)
                adapter.notifyDataSetChanged()
                loadCounters()
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Toast.makeText(this@MainActivity, "Ошибка загрузки: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun loadCounters() = lifecycleScope.launch(Dispatchers.IO) {
        try {
            val counters = RetrofitClient.getInstance().getCounters()
            withContext(Dispatchers.Main) {
                tvDayCounter.text = "Действий сегодня: ${counters.day}"
                tvTotalCounter.text = "Всего действий: ${counters.total}"
            }
        } catch (e: Exception) {
            // игнорируем
        }
    }

    private fun showAddTaskDialog() {
        val editText = EditText(this)
        editText.hint = "Введите задачу"
        AlertDialog.Builder(this)
            .setTitle("Новая задача")
            .setView(editText)
            .setPositiveButton("Добавить") { _, _ ->
                val text = editText.text.toString().trim()
                if (text.isNotEmpty()) {
                    addTask(text)
                }
            }
            .setNegativeButton("Отмена", null)
            .show()
    }

    @SuppressLint("DefaultLocale")
    private fun addTask(taskText: String) = lifecycleScope.launch(Dispatchers.IO) {
        try {
            val now = java.util.Calendar.getInstance()
            val dateStr = String.format("%04d-%02d-%02d", now.get(java.util.Calendar.YEAR), now.get(java.util.Calendar.MONTH)+1, now.get(java.util.Calendar.DAY_OF_MONTH))
            val timeStr = String.format("%02d:%02d", now.get(java.util.Calendar.HOUR_OF_DAY), now.get(java.util.Calendar.MINUTE))
            val fullTask = "$dateStr $timeStr $taskText"

            val currentTasks = tasks.toList()
            val newTasks = currentTasks + fullTask
            RetrofitClient.getInstance().updateTasks(newTasks)

            withContext(Dispatchers.Main) {
                loadData()
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Toast.makeText(this@MainActivity, "Ошибка добавления: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun deleteTask(position: Int) = lifecycleScope.launch(Dispatchers.IO)
    {
        try {
            val currentTasks = tasks.toList()
            val newTasks = currentTasks.toMutableList().apply { removeAt(position) }
            RetrofitClient.getInstance().updateTasks(newTasks)
            withContext(Dispatchers.Main) {
                loadData()
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Toast.makeText(this@MainActivity, "Ошибка удаления: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
}