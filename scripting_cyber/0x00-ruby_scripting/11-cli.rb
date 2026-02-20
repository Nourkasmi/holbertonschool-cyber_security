#!/usr/bin/env ruby
require 'optparse'
require 'fileutils'

TASK_FILE = 'tasks.txt'

options = {}

parser = OptionParser.new do |opts|
  opts.banner = "Usage: cli.rb [options]"

  opts.on("-a", "--add TASK", "Add a new task") do |task|
    options[:add] = task
  end

  opts.on("-l", "--list", "List all tasks") do
    options[:list] = true
  end

  opts.on("-r", "--remove INDEX", Integer, "Remove a task by index") do |index|
    options[:remove] = index
  end

  opts.on("-h", "--help", "Show help") do
    puts opts
    exit
  end
end

parser.parse!

FileUtils.touch(TASK_FILE)

if options[:add]
  File.open(TASK_FILE, 'a') { |f| f.puts options[:add] }
  puts "Task '#{options[:add]}' added."

elsif options[:list]
  tasks = File.readlines(TASK_FILE, chomp: true)
  tasks.each_with_index do |task, index|
    puts "#{index + 1}. #{task}"
  end

elsif options[:remove]
  tasks = File.readlines(TASK_FILE, chomp: true)
  index = options[:remove] - 1

  if index >= 0 && index < tasks.length
    removed = tasks.delete_at(index)
    File.write(TASK_FILE, tasks.join("\n") + (tasks.empty? ? "" : "\n"))
    puts "Task '#{removed}' removed."
  else
    puts "Invalid index."
  end

else
  puts parser
end