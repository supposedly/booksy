import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MyHoldsComponent } from './my-holds.component';

describe('MyHoldsComponent', () => {
  let component: MyHoldsComponent;
  let fixture: ComponentFixture<MyHoldsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MyHoldsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MyHoldsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
