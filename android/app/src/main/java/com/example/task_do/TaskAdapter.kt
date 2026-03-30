package com.example.task_do

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class TaskAdapter(
    private val tasks: List<String>,
    private val onDelete: (Int) -> Unit
) : RecyclerView.Adapter<TaskAdapter.TaskViewHolder>() {

    class TaskViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvTask: TextView = itemView.findViewById(R.id.tvTask)
        val btnDelete: Button = itemView.findViewById(R.id.btnDelete)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TaskViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_task, parent, false)
        return TaskViewHolder(view)
    }

    override fun onBindViewHolder(holder: TaskViewHolder, position: Int) {
        val task = tasks[position]
        val match = Regex("^\\d{4}-\\d{2}-\\d{2} (\\d{2}:\\d{2}) (.*)$").find(task)
        holder.tvTask.text = if (match != null) "${match.groupValues[1]} ${match.groupValues[2]}" else task
        holder.btnDelete.setOnClickListener { onDelete(position) }
    }

    override fun getItemCount() = tasks.size
}