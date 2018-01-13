import { Component, OnInit, Input } from '@angular/core';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.css']
})
export class NotificationsComponent implements OnInit {
  
  constructor(
    public globals: Globals,
    private memberService: MemberService
  ) {}
  
  @Input() username: string;
  
  ngOnChanges() { }
  
  ngOnInit() {
    if (this.globals.checkoutMessages === null) {
      this.memberService.getNotifs(this.username)
        .subscribe(resp => this.globals.checkoutMessages = resp);
    }
  }

}
