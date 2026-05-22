// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from social_robot_interfaces:srv/Tours.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "social_robot_interfaces/srv/detail/tours__rosidl_typesupport_introspection_c.h"
#include "social_robot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "social_robot_interfaces/srv/detail/tours__functions.h"
#include "social_robot_interfaces/srv/detail/tours__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  social_robot_interfaces__srv__Tours_Request__init(message_memory);
}

void social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_fini_function(void * message_memory)
{
  social_robot_interfaces__srv__Tours_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_member_array[1] = {
  {
    "idx",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT64,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(social_robot_interfaces__srv__Tours_Request, idx),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_members = {
  "social_robot_interfaces__srv",  // message namespace
  "Tours_Request",  // message name
  1,  // number of fields
  sizeof(social_robot_interfaces__srv__Tours_Request),
  social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_member_array,  // message members
  social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_type_support_handle = {
  0,
  &social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_social_robot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, srv, Tours_Request)() {
  if (!social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_type_support_handle.typesupport_identifier) {
    social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &social_robot_interfaces__srv__Tours_Request__rosidl_typesupport_introspection_c__Tours_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "social_robot_interfaces/srv/detail/tours__rosidl_typesupport_introspection_c.h"
// already included above
// #include "social_robot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "social_robot_interfaces/srv/detail/tours__functions.h"
// already included above
// #include "social_robot_interfaces/srv/detail/tours__struct.h"


// Include directives for member types
// Member `tour`
#include "geometry_msgs/msg/pose_stamped.h"
// Member `tour`
#include "geometry_msgs/msg/detail/pose_stamped__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  social_robot_interfaces__srv__Tours_Response__init(message_memory);
}

void social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_fini_function(void * message_memory)
{
  social_robot_interfaces__srv__Tours_Response__fini(message_memory);
}

size_t social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__size_function__Tours_Response__tour(
  const void * untyped_member)
{
  const geometry_msgs__msg__PoseStamped__Sequence * member =
    (const geometry_msgs__msg__PoseStamped__Sequence *)(untyped_member);
  return member->size;
}

const void * social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__get_const_function__Tours_Response__tour(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__PoseStamped__Sequence * member =
    (const geometry_msgs__msg__PoseStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void * social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__get_function__Tours_Response__tour(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__PoseStamped__Sequence * member =
    (geometry_msgs__msg__PoseStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__fetch_function__Tours_Response__tour(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__PoseStamped * item =
    ((const geometry_msgs__msg__PoseStamped *)
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__get_const_function__Tours_Response__tour(untyped_member, index));
  geometry_msgs__msg__PoseStamped * value =
    (geometry_msgs__msg__PoseStamped *)(untyped_value);
  *value = *item;
}

void social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__assign_function__Tours_Response__tour(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__PoseStamped * item =
    ((geometry_msgs__msg__PoseStamped *)
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__get_function__Tours_Response__tour(untyped_member, index));
  const geometry_msgs__msg__PoseStamped * value =
    (const geometry_msgs__msg__PoseStamped *)(untyped_value);
  *item = *value;
}

bool social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__resize_function__Tours_Response__tour(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__PoseStamped__Sequence * member =
    (geometry_msgs__msg__PoseStamped__Sequence *)(untyped_member);
  geometry_msgs__msg__PoseStamped__Sequence__fini(member);
  return geometry_msgs__msg__PoseStamped__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_member_array[1] = {
  {
    "tour",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(social_robot_interfaces__srv__Tours_Response, tour),  // bytes offset in struct
    NULL,  // default value
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__size_function__Tours_Response__tour,  // size() function pointer
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__get_const_function__Tours_Response__tour,  // get_const(index) function pointer
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__get_function__Tours_Response__tour,  // get(index) function pointer
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__fetch_function__Tours_Response__tour,  // fetch(index, &value) function pointer
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__assign_function__Tours_Response__tour,  // assign(index, value) function pointer
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__resize_function__Tours_Response__tour  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_members = {
  "social_robot_interfaces__srv",  // message namespace
  "Tours_Response",  // message name
  1,  // number of fields
  sizeof(social_robot_interfaces__srv__Tours_Response),
  social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_member_array,  // message members
  social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_type_support_handle = {
  0,
  &social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_social_robot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, srv, Tours_Response)() {
  social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, PoseStamped)();
  if (!social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_type_support_handle.typesupport_identifier) {
    social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &social_robot_interfaces__srv__Tours_Response__rosidl_typesupport_introspection_c__Tours_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "social_robot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "social_robot_interfaces/srv/detail/tours__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_service_members = {
  "social_robot_interfaces__srv",  // service namespace
  "Tours",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_Request_message_type_support_handle,
  NULL  // response message
  // social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_Response_message_type_support_handle
};

static rosidl_service_type_support_t social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_service_type_support_handle = {
  0,
  &social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, srv, Tours_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, srv, Tours_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_social_robot_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, srv, Tours)() {
  if (!social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_service_type_support_handle.typesupport_identifier) {
    social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, srv, Tours_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, social_robot_interfaces, srv, Tours_Response)()->data;
  }

  return &social_robot_interfaces__srv__detail__tours__rosidl_typesupport_introspection_c__Tours_service_type_support_handle;
}
