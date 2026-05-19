// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from social_robot_interfaces:srv/Tours.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__TRAITS_HPP_
#define SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "social_robot_interfaces/srv/detail/tours__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace social_robot_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const Tours_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: idx
  {
    out << "idx: ";
    rosidl_generator_traits::value_to_yaml(msg.idx, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Tours_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: idx
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "idx: ";
    rosidl_generator_traits::value_to_yaml(msg.idx, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Tours_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace social_robot_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use social_robot_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const social_robot_interfaces::srv::Tours_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  social_robot_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use social_robot_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const social_robot_interfaces::srv::Tours_Request & msg)
{
  return social_robot_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<social_robot_interfaces::srv::Tours_Request>()
{
  return "social_robot_interfaces::srv::Tours_Request";
}

template<>
inline const char * name<social_robot_interfaces::srv::Tours_Request>()
{
  return "social_robot_interfaces/srv/Tours_Request";
}

template<>
struct has_fixed_size<social_robot_interfaces::srv::Tours_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<social_robot_interfaces::srv::Tours_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<social_robot_interfaces::srv::Tours_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'tour'
#include "geometry_msgs/msg/detail/pose_stamped__traits.hpp"

namespace social_robot_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const Tours_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: tour
  {
    if (msg.tour.size() == 0) {
      out << "tour: []";
    } else {
      out << "tour: [";
      size_t pending_items = msg.tour.size();
      for (auto item : msg.tour) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Tours_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: tour
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.tour.size() == 0) {
      out << "tour: []\n";
    } else {
      out << "tour:\n";
      for (auto item : msg.tour) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Tours_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace social_robot_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use social_robot_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const social_robot_interfaces::srv::Tours_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  social_robot_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use social_robot_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const social_robot_interfaces::srv::Tours_Response & msg)
{
  return social_robot_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<social_robot_interfaces::srv::Tours_Response>()
{
  return "social_robot_interfaces::srv::Tours_Response";
}

template<>
inline const char * name<social_robot_interfaces::srv::Tours_Response>()
{
  return "social_robot_interfaces/srv/Tours_Response";
}

template<>
struct has_fixed_size<social_robot_interfaces::srv::Tours_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<social_robot_interfaces::srv::Tours_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<social_robot_interfaces::srv::Tours_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<social_robot_interfaces::srv::Tours>()
{
  return "social_robot_interfaces::srv::Tours";
}

template<>
inline const char * name<social_robot_interfaces::srv::Tours>()
{
  return "social_robot_interfaces/srv/Tours";
}

template<>
struct has_fixed_size<social_robot_interfaces::srv::Tours>
  : std::integral_constant<
    bool,
    has_fixed_size<social_robot_interfaces::srv::Tours_Request>::value &&
    has_fixed_size<social_robot_interfaces::srv::Tours_Response>::value
  >
{
};

template<>
struct has_bounded_size<social_robot_interfaces::srv::Tours>
  : std::integral_constant<
    bool,
    has_bounded_size<social_robot_interfaces::srv::Tours_Request>::value &&
    has_bounded_size<social_robot_interfaces::srv::Tours_Response>::value
  >
{
};

template<>
struct is_service<social_robot_interfaces::srv::Tours>
  : std::true_type
{
};

template<>
struct is_service_request<social_robot_interfaces::srv::Tours_Request>
  : std::true_type
{
};

template<>
struct is_service_response<social_robot_interfaces::srv::Tours_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__TRAITS_HPP_
