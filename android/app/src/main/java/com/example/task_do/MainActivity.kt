package com.example.task_do

import android.app.AlertDialog
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
import java.util.Calendar

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var tvDayCounter: TextView
    private lateinit var tvTotalCounter: TextView
    private lateinit var btnRefresh: Button
    private lateinit var fabAdd: FloatingActionButton

    private val tasks = mutableListOf<String>()
    private lateinit var adapter: TaskAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        tvDayCounter = findViewById(R.id.tvDayCounter)
        tvTotalCounter = findViewById(R.id.tvTotalCounter)
        btnRefresh = findViewById(R.id.btnRefresh)
        fabAdd = findViewById(R.id.fabAdd)

        adapter = TaskAdapter(tasks) { position ->
            deleteTask(position)
        }
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter

        fabAdd.setOnClickListener { showAddTaskDialog() }
        btnRefresh.setOnClickListener { loadData() }

        loadData()
    }

    private fun loadData() = lifecycleScope.launch(Dispatchers.IO) {
        try {
            val taskList = RetrofitClient.instance.getTasks()
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
            val counters = RetrofitClient.instance.getCounters()
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

    private fun addTask(taskText: String) = lifecycleScope.launch(Dispatchers.IO) {
        try {
            val now = Calendar.getInstance()
            val dateStr = String.format("%04d-%02d-%02d", now.get(Calendar.YEAR), now.get(Calendar.MONTH)+1, now.get(
                Calendar.DAY_OF_MONTH))
            val timeStr = String.format("%02d:%02d", now.get(Calendar.HOUR_OF_DAY), now.get(Calendar.MINUTE))
            val fullTask = "$dateStr $timeStr $taskText"

            val currentTasks = tasks.toList()
            val newTasks = currentTasks + fullTask
            RetrofitClient.instance.updateTasks(newTasks)

            withContext(Dispatchers.Main) {
                loadData()
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Toast.makeText(this@MainActivity, "Ошибка добавления: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun deleteTask(position: Int) = lifecycleScope.launch(Dispatchers.IO) {
        try {
            val currentTasks = tasks.toList()
            val newTasks = currentTasks.toMutableList().apply { removeAt(position) }
            RetrofitClient.instance.updateTasks(newTasks)
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