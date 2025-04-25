import React, { useEffect, useState } from "react";

import SidePanelCard from "./SidePanelCard";

function SidePanel() {
  const [threadHistoryData, setThreadHistoryData] = useState({
    today: [],
    week: [],
    month: [],
    earlier: [],
  });

  function getDate(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);

    return date;
  }

  useEffect(() => {
    const threadHistory = [
      {
        _id: "67dc32a9474c83a16dfee835",
        user_id: "janedoe",
        thread_id: "oCAMrUr8q3jJqlKjFIdEFwUOaPPVE4nf",
        date: "2025-03-20T15:22:17.578873+00:00",
        topic:
          "This is a test regarding your capabilities of using the code_interpreter",
        content: [],
      },
      {
        _id: "67dc331e474c83a16dfee836",
        user_id: "janedoe",
        thread_id: "noi8RsmgRMR99J3WZQ1SjNxfOEm9bQbj",
        date: "2025-03-20T15:24:14.604733+00:00",
        topic:
          "Please use the code_interpreter tool to run the following code exactly…",
        content: [],
      },
      {
        _id: "67dc335f474c83a16dfee838",
        user_id: "janedoe",
        thread_id: "yGNXGSIZuo3uKR0j93Ecs1PwrRi2XaNg",
        date: "2025-03-20T15:25:19.933795+00:00",
        topic:
          "Please assign the value 42 to the variable x in the code_interpreter t…",
        content: [],
      },
      {
        _id: "67dc3373474c83a16dfee839",
        user_id: "EMPTY USER!! TODO",
        thread_id: "Su5Gb1zfry4VDlFlBQ4rc7t6mto9vPfM",
        date: "2025-03-20T15:25:39.030140+00:00",
        topic:
          "Please generate a simple xarray dataset in the code_interpreter tool a…",
        content: [],
      },
      {
        _id: "67dc3381474c83a16dfee83a",
        user_id: "EMPTY USER!! TODO",
        thread_id: "YHy8XVXKW6iuXTb92HdQUQias1vuCdy4",
        date: "2025-03-20T15:25:53.942734+00:00",
        topic:
          "This is a test request for your basic functionality. Please respond wi…",
        content: [],
      },
      {
        _id: "67dc3385474c83a16dfee83b",
        user_id: "EMPTY USER!! TODO",
        thread_id: "jEyscQg0oSHCfeMqDv8Vw0jqqYX8IRmt",
        date: "2025-03-20T15:25:57.145211+00:00",
        topic:
          "Please use the code_interpreter tool to run `print(2938429834 * 234987…",
        content: [],
      },
      {
        _id: "67dc3387474c83a16dfee83c",
        user_id: "EMPTY USER!! TODO",
        thread_id: "sCgb80ilU2tEvkPidKSU7rCflDvyhvR7",
        date: "2025-03-20T15:25:59.209398+00:00",
        topic:
          "Please use the code_interpreter tool to run the following code: ",
        content: [],
      },
      {
        _id: "67dc3389474c83a16dfee83d",
        user_id: "EMPTY USER!! TODO",
        thread_id: "ufaIFpayMIuxvOPnQwetuf9ybZ7CMwpv",
        date: "2025-03-20T15:26:11.875477+00:00",
        topic:
          "Test: did the conversation continue after stopping the tool call?",
        content: [],
      },
    ];

    const today = getDate(0);
    const weekDay = getDate(7);
    const monthDay = getDate(30);

    const threadDict = { today: [], week: [], month: [], earlier: [] };

    threadDict.today = threadHistory.filter(
      (elem) => new Date(Date.parse(elem.date)) === today
    );
    threadDict.week = threadHistory.filter(
      (elem) =>
        new Date(Date.parse(elem.date)) < today &&
        new Date(Date.parse(elem.date)) >= weekDay
    );
    threadDict.month = threadHistory.filter(
      (elem) =>
        new Date(Date.parse(elem.date)) < weekDay &&
        new Date(Date.parse(elem.date)) >= monthDay
    );
    threadDict.earlier = threadHistory.filter(
      (elem) => new Date(Date.parse(elem.date)) < monthDay
    );

    setThreadHistoryData(threadDict);
  }, []);

  return (
    <>
      <SidePanelCard title="Today" data={threadHistoryData.today} />
      <SidePanelCard title="Last 7 days" data={threadHistoryData.week} />
      <SidePanelCard title="Last 30 days" data={threadHistoryData.month} />
      <SidePanelCard title="Earlier" data={threadHistoryData.earlier} />
    </>
  );
}

export default SidePanel;
