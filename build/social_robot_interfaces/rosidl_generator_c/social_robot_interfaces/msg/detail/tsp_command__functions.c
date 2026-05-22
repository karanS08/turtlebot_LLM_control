// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from social_robot_interfaces:msg/TspCommand.idl
// generated code does not contain a copyright notice
#include "social_robot_interfaces/msg/detail/tsp_command__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `waypoints`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
social_robot_interfaces__msg__TspCommand__init(social_robot_interfaces__msg__TspCommand * msg)
{
  if (!msg) {
    return false;
  }
  // waypoints
  if (!rosidl_runtime_c__int64__Sequence__init(&msg->waypoints, 0)) {
    social_robot_interfaces__msg__TspCommand__fini(msg);
    return false;
  }
  return true;
}

void
social_robot_interfaces__msg__TspCommand__fini(social_robot_interfaces__msg__TspCommand * msg)
{
  if (!msg) {
    return;
  }
  // waypoints
  rosidl_runtime_c__int64__Sequence__fini(&msg->waypoints);
}

bool
social_robot_interfaces__msg__TspCommand__are_equal(const social_robot_interfaces__msg__TspCommand * lhs, const social_robot_interfaces__msg__TspCommand * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // waypoints
  if (!rosidl_runtime_c__int64__Sequence__are_equal(
      &(lhs->waypoints), &(rhs->waypoints)))
  {
    return false;
  }
  return true;
}

bool
social_robot_interfaces__msg__TspCommand__copy(
  const social_robot_interfaces__msg__TspCommand * input,
  social_robot_interfaces__msg__TspCommand * output)
{
  if (!input || !output) {
    return false;
  }
  // waypoints
  if (!rosidl_runtime_c__int64__Sequence__copy(
      &(input->waypoints), &(output->waypoints)))
  {
    return false;
  }
  return true;
}

social_robot_interfaces__msg__TspCommand *
social_robot_interfaces__msg__TspCommand__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  social_robot_interfaces__msg__TspCommand * msg = (social_robot_interfaces__msg__TspCommand *)allocator.allocate(sizeof(social_robot_interfaces__msg__TspCommand), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(social_robot_interfaces__msg__TspCommand));
  bool success = social_robot_interfaces__msg__TspCommand__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
social_robot_interfaces__msg__TspCommand__destroy(social_robot_interfaces__msg__TspCommand * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    social_robot_interfaces__msg__TspCommand__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
social_robot_interfaces__msg__TspCommand__Sequence__init(social_robot_interfaces__msg__TspCommand__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  social_robot_interfaces__msg__TspCommand * data = NULL;

  if (size) {
    data = (social_robot_interfaces__msg__TspCommand *)allocator.zero_allocate(size, sizeof(social_robot_interfaces__msg__TspCommand), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = social_robot_interfaces__msg__TspCommand__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        social_robot_interfaces__msg__TspCommand__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
social_robot_interfaces__msg__TspCommand__Sequence__fini(social_robot_interfaces__msg__TspCommand__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      social_robot_interfaces__msg__TspCommand__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

social_robot_interfaces__msg__TspCommand__Sequence *
social_robot_interfaces__msg__TspCommand__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  social_robot_interfaces__msg__TspCommand__Sequence * array = (social_robot_interfaces__msg__TspCommand__Sequence *)allocator.allocate(sizeof(social_robot_interfaces__msg__TspCommand__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = social_robot_interfaces__msg__TspCommand__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
social_robot_interfaces__msg__TspCommand__Sequence__destroy(social_robot_interfaces__msg__TspCommand__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    social_robot_interfaces__msg__TspCommand__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
social_robot_interfaces__msg__TspCommand__Sequence__are_equal(const social_robot_interfaces__msg__TspCommand__Sequence * lhs, const social_robot_interfaces__msg__TspCommand__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!social_robot_interfaces__msg__TspCommand__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
social_robot_interfaces__msg__TspCommand__Sequence__copy(
  const social_robot_interfaces__msg__TspCommand__Sequence * input,
  social_robot_interfaces__msg__TspCommand__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(social_robot_interfaces__msg__TspCommand);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    social_robot_interfaces__msg__TspCommand * data =
      (social_robot_interfaces__msg__TspCommand *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!social_robot_interfaces__msg__TspCommand__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          social_robot_interfaces__msg__TspCommand__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!social_robot_interfaces__msg__TspCommand__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
