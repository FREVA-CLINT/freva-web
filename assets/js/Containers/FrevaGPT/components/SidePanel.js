import React, { useEffect, useState } from "react";

import SidePanelCard from "./SidePanelCard";

function SidePanel() {
  const [threadData, setThreadData] = useState([]);

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
    ];

    setThreadData(threadHistory);
  }, []);

  return (
    <>
      <SidePanelCard title="Today" data={threadData} />
      <SidePanelCard title="Last 7 days" data={[]} />
      <SidePanelCard title="Last 30 days" data={[]} />
      <SidePanelCard title="Earlier" data={[]} />
    </>
  );
}

export default SidePanel;
