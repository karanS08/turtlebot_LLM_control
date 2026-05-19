#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to social_robot_interfaces__srv__Tours_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Tours_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub idx: i64,

}



impl Default for Tours_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Tours_Request::default())
  }
}

impl rosidl_runtime_rs::Message for Tours_Request {
  type RmwMsg = super::srv::rmw::Tours_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        idx: msg.idx,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      idx: msg.idx,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      idx: msg.idx,
    }
  }
}


// Corresponds to social_robot_interfaces__srv__Tours_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Tours_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub tour: Vec<geometry_msgs::msg::PoseStamped>,

}



impl Default for Tours_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Tours_Response::default())
  }
}

impl rosidl_runtime_rs::Message for Tours_Response {
  type RmwMsg = super::srv::rmw::Tours_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        tour: msg.tour
          .into_iter()
          .map(|elem| geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        tour: msg.tour
          .iter()
          .map(|elem| geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      tour: msg.tour
          .into_iter()
          .map(geometry_msgs::msg::PoseStamped::from_rmw_message)
          .collect(),
    }
  }
}






#[link(name = "social_robot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__social_robot_interfaces__srv__Tours() -> *const std::ffi::c_void;
}

// Corresponds to social_robot_interfaces__srv__Tours
#[allow(missing_docs, non_camel_case_types)]
pub struct Tours;

impl rosidl_runtime_rs::Service for Tours {
    type Request = Tours_Request;
    type Response = Tours_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__social_robot_interfaces__srv__Tours() }
    }
}


